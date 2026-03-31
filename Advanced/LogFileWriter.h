#ifndef LOG_FILE_WRITER_H
#define LOG_FILE_WRITER_H

//Including <queue> gives you access to std::queue, which is a FIFO (First-In, First-Out) container adapter
#include <queue>

// Needed by linux g++ compiler
#include <string>
#include <condition_variable>
#include <thread>
#include <atomic>

class LogFileWriter {

    public:

        // Keep the enum for internal C++ use
        enum LogLevel { DEBUG = 0, INFO = 1, WARN = 2, ERROR = 3, FATAL = 4 };

        // Internal C++ macro-friendly log.
        // __FILE__ returns a literal string char*, the parameter is const std::string& p_file
        void _log_internal(LogLevel p_level, const std::string& p_msg, const std::string& p_file, int p_line, bool isStdOutput);

        // Generic log function and the log_level setter exported to PYTHON
        // Sets the minimum log level below which logs are not stored
        void set_min_level(int p_level);

        // LogFileWriter is a singleton; this is the method that returns the single instance of the object.
        // If it is nullptr, it is instantiated.
        static LogFileWriter* get_singleton() { 
            if (singleton == nullptr) {
                singleton = new LogFileWriter(); // Se crea aquí la primera vez
            }
            return singleton;
        }

        // Constructor & Destructor
        LogFileWriter();
        ~LogFileWriter();

    private:

        // Log input object structure
        struct LogEntry {
            int level;                  // LOG level
            std::string message;        // LOG message
            std::string timestamp;      // LOG timestamp
            std::string file;           // File in which the message is thrown
            int line;                   // File's line in which the message is thrown
            bool isStdOutput;           // The message should be stream to the standard output ?
        };

        // Singleton pointer
        static inline LogFileWriter* singleton = nullptr;

        //std::atomic<int> ensures that the operation happens as a single, indivisible unit.
        std::atomic<int> min_level{0};
    
        // FIFO queue of LogEntry objects
        std::queue<LogEntry> log_queue;

        // Building a Thread-Safe Queue.
        std::mutex queue_mutex;

        // Final piece to the puzzle for a high-performance Producer-Consumer system!
        std::condition_variable cv;

        // object that actually runs your code in parallel.
        std::thread worker_thread;

        //std::atomic<int> ensures that the operation happens as a single, indivisible unit.
        std::atomic<bool> should_exit{false};

        // private methods
        // Method that manages the writing of a log when it occurs
        void process_logs();

        // a method that provides us with the date professionally
        std::string get_timestamp();
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