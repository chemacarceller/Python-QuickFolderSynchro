#ifndef LOG_FILE_WRITER_H
#define LOG_FILE_WRITER_H

// C++ library designed to simplify inter-process communication (IPC) and synchronization
#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/containers/string.hpp>
#include <boost/interprocess/containers/deque.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include <boost/interprocess/sync/interprocess_mutex.hpp>
#include <boost/interprocess/sync/interprocess_condition.hpp>

#include <atomic>
#include <thread>
#include <iostream>
#include <iomanip>


using namespace boost::interprocess;

// An allocator is an object that manages how and where memory is reserved for your data.
// Allocator for strings
typedef allocator<char, managed_shared_memory::segment_manager> CharAlloc;
typedef basic_string<char, std::char_traits<char>, CharAlloc> shared_string;

// Estructura de Log compatible
struct LogEntry {
    int level;
    shared_string message;
    shared_string timestamp;
    shared_string file;
    int line;
    bool isStdOutput;

    // Constructor needed to initialize strings in shared memory
    LogEntry(managed_shared_memory::segment_manager* sm) : message(sm), timestamp(sm), file(sm) {}
};

// Allocator for the Logs queue
typedef allocator<LogEntry, managed_shared_memory::segment_manager> LogEntryAlloc;
typedef deque<LogEntry, LogEntryAlloc> SharedLogQueue;

// Data structure that is stored in shared memory
struct SharedLogState {
    SharedLogQueue log_queue;
    interprocess_mutex queue_mutex;
    interprocess_condition cv;
    std::atomic<int> min_level;
    std::atomic<bool> should_exit;
    std::atomic<int> process_count = 0;

    SharedLogState(managed_shared_memory::segment_manager* sm) : log_queue(sm), min_level(0), should_exit(false) { process_count=0; }
};

// This class is a singleton for managing a log file in a way that uses a shared memory area between different processes
// Each process will have a singleton object, but the message queue is common to all processes
// The thread that manages file writing is only configured in the main process, while in the rest of the processes, although it exists, it is not used for anything
class LogFileWriter {

    private :

        // Pointer to the data structure stored in shared memory
        SharedLogState* state;

        // Thread responsible for writing to the log file
        std::thread worker_thread;

        // It represents the shared memory segment
        managed_shared_memory segment;

        // Method that manages the writing of a log when it occurs. The thread of execution is the one that executes this method
        void process_logs();

        // Method that provides us with the date
        std::string get_timestamp();

        // Singleton pointer
        static inline LogFileWriter* singleton = nullptr;

    public:

        // Keep the enum for internal C++ use
        enum LogLevel { DEBUG = 0, INFO = 1, WARN = 2, ERROR = 3, FATAL = 4 };

        LogFileWriter();
        ~LogFileWriter();

        // Sets the minimum log level below which logs are not stored
        void set_min_level(int p_level);

        // It is used to initialize the thread of execution to write to the file, only in the parent process; in the other processes this method is not launched, so the variable remains unused.
        void start_worker();

        // It is used to free up resources; it is the replacement for the destructor that is not executed.
        // It is called from all Python processes configured as atexit.register()
        void freeze();

        // It will give us one singleton instance per process
        static LogFileWriter* get_singleton() { 
            if (singleton == nullptr) {
                singleton = new LogFileWriter(); 
            }
            
            return singleton;
        }
        
        // Function to write log entries to the FIFO list; each process executes its own method
        void _log_internal(LogLevel p_level, const std::string& p_msg, const std::string& p_file, int p_line, bool isStdOutput);
};


// C++ Helper Macros. To use in pure C++
#define LOG_DEBUG(m, file, line, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::DEBUG, (m), file, line, isStdOutput)))

#define LOG_INFO(m, file, line, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::INFO, (m), file, line, isStdOutput)))

#define LOG_WARN(m, file, line, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::WARN, (m), file, line, isStdOutput)))

#define LOG_ERROR(m, file, line, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::ERROR, (m), file, line, isStdOutput)))

#define LOG_FATAL(m, file, line, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::FATAL, (m), file, line, isStdOutput)))

#endif