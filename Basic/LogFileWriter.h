#ifndef LOG_FILE_WRITER_H
#define LOG_FILE_WRITER_H

#include <string>
#include <fstream>

class LogFileWriter {

    private:

        // Contains the name of the file to manage
        std::string _filename;
        std::ofstream _file;

    public:

        // Constructor
        LogFileWriter(const std::string &filename, bool isMainProcess);
        ~LogFileWriter();

        void write_line(const std::string &text);

        // Getters and Setters
        void set_filename(std::string p_filename) { _filename = p_filename; }
        std::string get_filename() const { return _filename; }

    };

#endif