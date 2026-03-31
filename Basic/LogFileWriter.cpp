#include "LogFileWriter.h"

#include <iostream>

// For using it in Python 
#include <pybind11/pybind11.h>
namespace py = pybind11;


LogFileWriter::LogFileWriter(const std::string &filename, bool isMainProcess) : _filename(filename) {
    if (isMainProcess) {
        try {
            // Opening file for writing, that means creates the file or resets it only father process
            _file.open(_filename);
            _file.close();
        } catch (const std::ios_base::failure& e) {

            // Capturar el error específico de I/O
            std::cerr << "Error crítico de archivo: " << e.what() << std::endl;

            // Re-lanzamos una excepción más descriptiva para Python (pybind11 la capturará)
            throw std::runtime_error("No se pudo abrir o escribir en: " + _filename);
        }
    }
}

LogFileWriter::~LogFileWriter() {
    if (_file.is_open()) _file.close();
}

void LogFileWriter::write_line(const std::string &text) {

    try {
        // Opening the file in append mode, writes and closes
        _file.open(_filename, std::ios::app);

        if (_file.is_open()) {
            // Writes the text
            // Inserts a newline character (\n), moving the cursor to the next line.
            // Performs a flush
            _file << text << std::endl;
            _file.flush();
        }

        // Closes the file
        _file.close();

     } catch (const std::ios_base::failure& e) {

            // Capturar el error específico de I/O
            std::cerr << "Error crítico de archivo: " << e.what() << std::endl;

            // Re-lanzamos una excepción más descriptiva para Python (pybind11 la capturará)
            throw std::runtime_error("No se pudo abrir o escribir en: " + _filename);
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
    .def(py::init<const std::string &, bool>()) // Bind constructor
    //This binds a specific member function.
    .def("write_line", &LogFileWriter::write_line); // Bind method
}
