#include "LogFileWriter.h"


// For using it in Python 
#include <pybind11/pybind11.h>
namespace py = pybind11;


LogFileWriter::LogFileWriter(const std::string &filename) : _filename(filename) {
    // Opening file for writing, that means creates the file or resets it
    std::ofstream file(filename);
    file.close();
}

void LogFileWriter::write_line(const std::string &text) {
    // Opening the file in append mode, writes and closes
    std::ofstream file(_filename, std::ios::app);

    if (file.is_open()) {
        // Writes the text
        // Inserts a newline character (\n), moving the cursor to the next line.
        // Performs a flush
        file << text << std::endl;

        // Closes the file
        file.close();
    }
}


// Create the Python module
//This code is the "bridge" that exports your C++ code as a Python module
//This defines the module name

PYBIND11_MODULE(LogFileWriter, m) {
    // This exposes your C++ class LogFileWriter to Python
    // In Python, the class will be renamed to Writer. Usage: obj = LogFileWriter.Writer("test.txt").
    py::class_<LogFileWriter>(m, "Writer")
    //This binds the constructor.
    .def(py::init<const std::string &>()) // Bind constructor
    //This binds a specific member function.
    .def("write_line", &LogFileWriter::write_line); // Bind method
}
