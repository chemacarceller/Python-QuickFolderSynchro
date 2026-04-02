#include "LogFileWriter.h"

#include <fstream>
#include <chrono>

// For using it in Python 
#include <pybind11/pybind11.h>
namespace py = pybind11;


// Log file name defined as constant
static const char* LOG_FILENAME = "QuickFolderSynchroAdvancedPlus.log";

// Translates your internal enum values into human-readable text for your log file.
// It is used to generate the string that will be stored with respect to the enum
const char* levels[] = {"DEBUG", "INFO", "WARN", "ERROR", "FATAL"};

// The Operating System reserves 1MB (1024×1024 bytes) of physical RAM, assigning it the name "LogFileWriterShm"
// The segment object initializes the internal memory manager
// If the segment already exists, it is simply assigned to the state variable.
LogFileWriter::LogFileWriter() : segment(open_or_create, "LogFileWriterShm", 1024 * 1024) 
{
    // Gets the state object or constructs it if it does not exist
    state = segment.find_or_construct<SharedLogState>("SharedState")(segment.get_segment_manager());

    // Increase the number of references to the shared memory, that is, the number of processes that have access to the shared memory.
    state->process_count++;
    
    // Assign the object to the singleton variable
    singleton = this;
}


// I don't know why, but when a process finishes, it doesn't call the destructor.
// I've made it so that when exiting a Python process, the freeze function is called and it works
LogFileWriter::~LogFileWriter() { }


// Method that replaces the destructor 
void LogFileWriter::freeze() {

    // Decrements references to shared memory
    state->process_count--;

    // If the number of references is zero
    if (state) {
        if (state->process_count == 0) {
            try {

                // We block it to ensure the thread receives the signal
                {
                    scoped_lock<interprocess_mutex> lock(state->queue_mutex);
                    state->should_exit = true;
                }

                // We woke up to the thread
                state->cv.notify_all();
            

                // We're waiting for the thread. If you don't use join(), std::thread will terminate.
                if (worker_thread.joinable()) {worker_thread.join(); }

                // ONLY NOW do we erase the shared memory
                segment.destroy<SharedLogState>("SharedState");
                shared_memory_object::remove("LogFileWriterShm");

            } catch (...) {
                // You guarantee that, whatever happens inside the destructor (freeze function), the thread of execution will continue its exit path peacefully.
            }
        }
    }

    // When we close, we also set the pointer to nullptr
    if (singleton == this) singleton = nullptr;
}


// This method starts the worker thread that will process the logs in the background
void LogFileWriter::start_worker() {

    if (!worker_thread.joinable()) worker_thread = std::thread(&LogFileWriter::process_logs, this);

    // We create the empty file so we can add to it, taking advantage of the fact that this method only runs in the main process.
    std::ofstream file(LOG_FILENAME, std::ios::trunc);
    if (file.is_open()) file.close();
}


// Function that sets the minimum level from which logs will be saved
void LogFileWriter::set_min_level(int p_level) { state->min_level = p_level; }


// C++ method to put an item in the FIFO of LogEntry and wake up the process_logs method to write the item
void LogFileWriter::_log_internal(LogLevel p_level, const std::string& p_msg, const std::string& p_file, int p_line, bool isStdOutput) 
{

    // Their job is to prevent the system from wasting time processing messages that the user has decided to ignore.
    if ((int)p_level < state->min_level) return;

    // We block the message queue to have exclusive access
    scoped_lock<interprocess_mutex> lock(state->queue_mutex);
        
    // We create the LogEntry using the shared memory manager
    LogEntry entry(segment.get_segment_manager());

    // We save the information in the log input object
    entry.level = p_level;
    entry.message = p_msg.c_str();
    entry.timestamp = get_timestamp().c_str();
    entry.file = p_file.c_str();
    entry.line = p_line;
    entry.isStdOutput = isStdOutput;

    // We save the log entry in the FIFO queue
    state->log_queue.push_back(entry);

    // We wake up the execution thread so that it writes to the log file
    state->cv.notify_one(); 
    
}


void LogFileWriter::process_logs() {

    // Abrir el fichero de logs para añadir entradas
    std::ofstream file(LOG_FILENAME, std::ios::app);

    while (true) {

        std::string output;

        {
            // We block the FIFO queue to have exclusive access
            scoped_lock<interprocess_mutex> lock(state->queue_mutex);
            
            // It goes to sleep if the queue is empty and it shouldn't leave, and it clears the message queue until it is woken up.
            // Once woken up, if there are messages in the queue, it will block the queue again.
            state->cv.wait(lock, [this]{ return !state->log_queue.empty() || state->should_exit;  });

            // It is used to exit the infinite loop when you decide to exit with should_exit
            if (state->should_exit && state->log_queue.empty()) break;

            // We access the following log entry to write it to the file
            LogEntry& entry = state->log_queue.front();

            // We generate the string to display on the screen and in the file
            std::ostringstream ss;
            ss << "[" << entry.timestamp << "] [" << levels[entry.level] << "] "
               << "[" << entry.file << ":" << entry.line << "] " << entry.message;
            output = ss.str();

            // is displayed on screen
            if (entry.level >= ERROR) std::cerr << output << std::endl;
            else if (entry.isStdOutput) std::cout << output << std::endl;

            // We remove the entry from the FIFO queue
            state->log_queue.pop_front();

        }

         // Everything is Writing to file
        if (file.is_open()) {
            file << output << std::endl;
            file.flush();
        }
    }

    // The file is closed
    if (file.is_open()) file.close();
}


// Get the current date professionally
std::string LogFileWriter::get_timestamp() {

    // Using the modern C++ way to handle time
    // 1. Get the current time point
    auto now = std::chrono::system_clock::now();

    // 1. Get miliseconds
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;

    // 2. Convert to time_t for formatting
    auto t = std::chrono::system_clock::to_time_t(now);
    
    // 3. Thread-safe conversion to local time
    std::basic_ostringstream<char> ss;

    std::tm lt;
    #ifdef _WIN32
        localtime_s(&lt, &t); 
    #else
        localtime_r(&t, &lt);
    #endif

    // 4. The line you provided: format and "pipe" into the stream
    ss << std::put_time(&lt, "%H:%M:%S")<< '.' << std::setfill('0') << std::setw(3) << ms.count();

    // 5. Return as a std::string
    return std::string(ss.str());    
}



// Create the Python module
//This code is the "bridge" that exports your C++ code as a Python module
//This defines the module name

PYBIND11_MODULE(LogFileWriter, m) {

    // This exposes your C++ class LogFileWriter to Python
    // In Python, the class will be renamed to Writer. Usage: obj = LogFileWriter.Writer().
    py::class_<LogFileWriter>(m, "Writer")
    
    // exposing a Singleton pattern so that it can be used in Python.
    // In Python, you will get an object like ogger = LogFileWriter.Writer.get_instance()
    .def_static("get_instance", &LogFileWriter::get_singleton, py::return_value_policy::reference)
    
    // Non-static methods available in Python
    .def("set_min_level", &LogFileWriter::set_min_level)
    .def("start_worker", &LogFileWriter::start_worker)
    .def("freeze", &LogFileWriter::freeze)
    // Static methods available in Python; they call macros
    .def_static("LOG_DEBUG", [](std::string message, const std::string& p_file, int p_line, bool isStdOutput=true) { LOG_DEBUG(message, p_file, p_line, isStdOutput); }, py::arg("message"), py::arg("p_file")=__FILE__, py::arg("p_line")=__LINE__, py::arg("isStdOutput") = true)
    .def_static("LOG_INFO", [](std::string message, const std::string& p_file, int p_line, bool isStdOutput=true) { LOG_INFO(message, p_file, p_line, isStdOutput); }, py::arg("message"), py::arg("p_file")=__FILE__, py::arg("p_line")=__LINE__, py::arg("isStdOutput") = true)
    .def_static("LOG_WARN", [](std::string message, const std::string& p_file, int p_line, bool isStdOutput=true) { LOG_WARN(message, p_file, p_line, isStdOutput); }, py::arg("message"), py::arg("p_file")=__FILE__, py::arg("p_line")=__LINE__, py::arg("isStdOutput") = true)
    .def_static("LOG_ERROR", [](std::string message, const std::string& p_file, int p_line, bool isStdOutput=true) { LOG_ERROR(message, p_file, p_line, isStdOutput); }, py::arg("message"), py::arg("p_file")=__FILE__, py::arg("p_line")=__LINE__, py::arg("isStdOutput") = true)
    .def_static("LOG_FATAL", [](std::string message, const std::string& p_file, int p_line, bool isStdOutput=true) { LOG_FATAL(message, p_file, p_line, isStdOutput); }, py::arg("message"), py::arg("p_file")=__FILE__, py::arg("p_line")=__LINE__, py::arg("isStdOutput") = true);

    // This binds the enum values
    py::enum_<LogFileWriter::LogLevel>(m, "LogLevel")
        .value("DEBUG", LogFileWriter::LogLevel::DEBUG)
        .value("INFO", LogFileWriter::LogLevel::INFO)
        .value("WARN", LogFileWriter::LogLevel::WARN)
        .value("ERROR", LogFileWriter::LogLevel::ERROR)
        .value("FATAL", LogFileWriter::LogLevel::FATAL)
        .export_values();
}