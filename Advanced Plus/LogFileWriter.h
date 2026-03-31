#ifndef LOG_FILE_WRITER_H
#define LOG_FILE_WRITER_H

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

// Allocators
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

    // Constructor necesario para inicializar los strings en la memoria compartida
    LogEntry(managed_shared_memory::segment_manager* sm) : message(sm), timestamp(sm), file(sm) {}
};

// Allocator para la cola de Logs
typedef allocator<LogEntry, managed_shared_memory::segment_manager> LogEntryAlloc;
typedef deque<LogEntry, LogEntryAlloc> SharedLogQueue;

struct SharedLogState {
    SharedLogQueue log_queue;
    interprocess_mutex queue_mutex;
    interprocess_condition cv;
    std::atomic<int> min_level;
    std::atomic<bool> should_exit;
    std::atomic<int> process_count;

    SharedLogState(managed_shared_memory::segment_manager* sm) : log_queue(sm), min_level(0), should_exit(false) { process_count=0; }
};

class LogFileWriter {

    private:
        SharedLogState* state; // Puntero al bloque en RAM compartida
        std::thread worker_thread;
        managed_shared_memory segment;

        // Method that manages the writing of a log when it occurs
        void process_logs();

        // a method that provides us with the date professionally
        std::string get_timestamp();

    public:

        // Keep the enum for internal C++ use
        enum LogLevel { DEBUG = 0, INFO = 1, WARN = 2, ERROR = 3, FATAL = 4 };

        LogFileWriter();
        ~LogFileWriter();

        void set_min_level(int p_level);
        void start_worker();
        
        static LogFileWriter* get_singleton() {
            static LogFileWriter instance;
            return &instance;
        }
        
        void _log_internal(LogLevel p_level, const std::string& p_msg, const std::string& p_file, int p_line, bool isStdOutput);
};

// C++ Helper Macros. To use in pure C++
#define LOG_DEBUG(m, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::DEBUG, (m), __FILE__, __LINE__, isStdOutput)))

#define LOG_INFO(m, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::INFO, (m), __FILE__, __LINE__, isStdOutput)))

#define LOG_WARN(m, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::WARN, (m), __FILE__, __LINE__, isStdOutput)))

#define LOG_ERROR(m, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::ERROR, (m), __FILE__, __LINE__, isStdOutput)))

#define LOG_FATAL(m, isStdOutput) \
    ((void)(LogFileWriter::get_singleton()->_log_internal( \
        LogFileWriter::LogLevel::FATAL, (m), __FILE__, __LINE__, isStdOutput)))

#endif