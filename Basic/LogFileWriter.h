#ifndef LOG_FILE_WRITER_H
#define LOG_FILE_WRITER_H

#include <string>
#include <fstream>

class LogFileWriter {

    private:

        // Contains the name of the file and teh file object to be managed
        std::string _filename;
        std::ofstream _file;

    public:

        // Constructor & Destructor
        LogFileWriter(const std::string &filename, bool isMainProcess);
        ~LogFileWriter();

        // Exported method to write logs in file
        void write_line(const std::string &text);

        // Getters and Setters
        void set_filename(std::string p_filename) { _filename = p_filename; }
        std::string get_filename() const { return _filename; }

    };

#endif