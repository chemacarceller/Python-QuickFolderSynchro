#include "LogFileWriter.h"

#include <fstream>

// For using it in Python 
#include <pybind11/pybind11.h>
namespace py = pybind11;


// Log file name defined as constant
static const char* LOG_FILENAME = "QuickFolderSynchroPRO.log";

// Translates your internal enum values into human-readable text for your log file.
// It is used to generate the string that will be stored with respect to the enum
const char* levels[] = {"DEBUG", "INFO", "WARN", "ERROR", "FATAL"};

// Constructor: Initializes the shared memory segment and the shared state
LogFileWriter::LogFileWriter() : segment(open_or_create, "LogFileWriterShm", 1024 * 1024) 
{
    // Buscamos o creamos el estado compartido
    // El constructor de SharedLogState se llama solo la primera vez que se crea el segmento, luego se reutiliza
    state = segment.find_or_construct<SharedLogState>("SharedState")(segment.get_segment_manager());

    // Contador de referencias
    state->process_count++;
}


// MÉTODO CRÍTICO: Solo se debe llamar desde el proceso principal de Python
// Este método inicia el worker thread que se encargará de procesar los logs en segundo plano
void LogFileWriter::start_worker() {
    if (!worker_thread.joinable()) {
        worker_thread = std::thread(&LogFileWriter::process_logs, this);
    }

    // Creamos el archivo vacío para poder ir añadiendo
    std::ofstream file(LOG_FILENAME, std::ios::trunc);
    if (file.is_open()) file.close();
}

LogFileWriter::~LogFileWriter() {

    state->process_count--;

    if (state->process_count == 0) {

try {
        if (state) {

            // 1. Bloqueamos para asegurar que el hilo recibe la señal
            {
                scoped_lock<interprocess_mutex> lock(state->queue_mutex);
                state->should_exit = true;
            }
            // 2. Despertamos al hilo
            state->cv.notify_all();
        }

        // 3. ESPERAMOS al hilo. Si no haces join(), std::thread lanza 'terminate'
        if (worker_thread.joinable()) {
            worker_thread.join();
        }

        // 4. SOLO AHORA borramos la memoria compartida
        segment.destroy<SharedLogState>("LogState");
        shared_memory_object::remove("QuickFolderSynchro_SHM");

    } catch (...) {
        // Nunca permitas que una excepción salga del destructor
    }
    }

}


// Function that sets the minimum level from which logs will be saved
void LogFileWriter::set_min_level(int p_level) { state->min_level = p_level; }


// C++ method to put an item in the FIFO of LogEntry and wake up the process_logs method to write the item
void LogFileWriter::_log_internal(LogLevel p_level, const std::string& p_msg, const std::string& p_file, int p_line, bool isStdOutput) 
{

    // Their job is to prevent the system from wasting time processing messages that the user has decided to ignore.
    if ((int)p_level < state->min_level) return;

    scoped_lock<interprocess_mutex> lock(state->queue_mutex);
        
    // Creamos el LogEntry usando el manager de la memoria compartida
    LogEntry entry(segment.get_segment_manager());
    entry.level = p_level;
    entry.message = p_msg.c_str();
    entry.timestamp = get_timestamp().c_str();
    entry.file = p_file.c_str();
    entry.line = p_line;
    entry.isStdOutput = isStdOutput;

    state->cv.notify_one(); 
    state->log_queue.push_back(entry);
    
}



void LogFileWriter::process_logs() {
    std::ofstream file(LOG_FILENAME, std::ios::app);

    while (true) {

        scoped_lock<interprocess_mutex> lock(state->queue_mutex);
        
        // Espera hasta que haya logs O debamos salir
        state->cv.wait(lock, [this]{ 
            return !state->log_queue.empty() || state->should_exit; 
        });

        // Procesar TODO lo que haya en la cola actualmente
        while (!state->log_queue.empty()) {

            LogEntry& entry = state->log_queue.front();
            
            std::ostringstream ss;
            ss << "[" << entry.timestamp << "] [" << levels[entry.level] << "] "
               << "[" << entry.file << ":" << entry.line << "] " << entry.message;
            std::string output = ss.str();

            if (entry.level >= ERROR) std::cerr << output << std::endl;
            else if (entry.isStdOutput) std::cout << output << std::endl;

            if (file.is_open()) {
                file << output << std::endl;
            }
            
            state->log_queue.pop_front();
        }
        
        // Forzar escritura en disco para que no se quede en el búfer de C++
        if (file.is_open()) file.flush();

        // SALIDA: Solo si should_exit es true Y la cola está realmente vacía
        if (state->should_exit && state->log_queue.empty()) {
            break;
        }
    }
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
    
    //This binds the functions for logging
    .def("set_min_level", &LogFileWriter::set_min_level)
    .def("start_worker", &LogFileWriter::start_worker)
    .def_static("LOG_DEBUG", [](std::string message, bool isStdOutput=true) { LOG_DEBUG(message, isStdOutput); }, py::arg("message"), py::arg("isStdOutput") = true)
    .def_static("LOG_INFO", [](std::string message, bool isStdOutput=true) { LOG_INFO(message, isStdOutput); }, py::arg("message"), py::arg("isStdOutput") = true)
    .def_static("LOG_WARN", [](std::string message, bool isStdOutput=true) { LOG_WARN(message, isStdOutput); }, py::arg("message"), py::arg("isStdOutput") = true)
    .def_static("LOG_ERROR", [](std::string message, bool isStdOutput=true) { LOG_ERROR(message, isStdOutput); }, py::arg("message"), py::arg("isStdOutput") = true)
    .def_static("LOG_FATAL", [](std::string message, bool isStdOutput=true) { LOG_FATAL(message, isStdOutput); }, py::arg("message"), py::arg("isStdOutput") = true);

    // This binds the enum values
    py::enum_<LogFileWriter::LogLevel>(m, "LogLevel")
        .value("DEBUG", LogFileWriter::LogLevel::DEBUG)
        .value("INFO", LogFileWriter::LogLevel::INFO)
        .value("WARN", LogFileWriter::LogLevel::WARN)
        .value("ERROR", LogFileWriter::LogLevel::ERROR)
        .value("FATAL", LogFileWriter::LogLevel::FATAL)
        .export_values();
}