__author__ = 'tahsmith'

import sys
import argparse

import pyparsing
from cmake.parser import Parser


def handle_error_and_exit(source, error):
    print 'Error parsing {}: {}'.format(source, error)
    print pyparsing.line(error.loc, string)
    print (error.col - 1) * ' ' + '^'
    sys.exit(1)


if __name__ == '__main__':
    parser = Parser()
    filename = sys.argv[1]
    try:
        f = open(filename)
    except IOError:
        sys.exit(1)
    string = f.read()

    try:
        parser.file.parseString(string).asList()
    except pyparsing.ParseException as error:
        handle_error_and_exit(filename, error)
    except pyparsing.ParseSyntaxException as error:
        handle_error_and_exit(filename, error)

