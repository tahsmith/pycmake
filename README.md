# I can't believe it's not CMake!
[![Build Status](https://travis-ci.org/tahsmith/pycmake.svg?branch=master)](https://travis-ci.org/tahsmith/pycmake)
The beginings of a python based cmake interpreter.

## Usage

Currently there is a very basic read-evaluate-print loop:

    cmake.py --interactive

It is not yet useful. The extent of it so far it this:

    set(x "Hello, World!)
    message(${x})
