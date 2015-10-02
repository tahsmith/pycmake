# I can't believe it's not CMake!
The beginings of a python based cmake interpreter.

## Usage

### Interactive
Currently there is a very basic read-evaluate-print loop:

    cmake.py --interactive

It is not yet useful. The extent of it so far it this:

    set(x "Hello, World!)
    message(${x})
