#ifndef LOG_FILE_WRITER_H
#define LOG_FILE_WRITER_H

#include <fstream>
#include <string>

class LogFileWriter {

    private:

        // Contains the name of the file to manage
        std::string _filename;

    public:

        // Constructor
        LogFileWriter(const std::string &filename);

        void write_line(const std::string &text);

        // Getters and Setters
        void set_filename(std::string p_filename) { _filename = p_filename; }
        std::string get_filename() const { return _filename; }

    };

#endif