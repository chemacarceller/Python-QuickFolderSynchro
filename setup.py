from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        'LogFileWriter', # Nombre del módulo resultante
        ['LogFileWriter.cpp'],
        include_dirs=[pybind11.get_include()],
        language='c++',
        extra_compile_args=['/std:c++17'], # <--- Crucial para Windows
    ),
]

setup(name='LogFileWriter', ext_modules=ext_modules)