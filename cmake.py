__author__ = 'tahsmith'

import sys
import argparse

import pyparsing
from cmake.parser import Parser

parser = Parser()
f = open(sys.argv[1])
string = f.read()

try:
    print parser.file.parseString(string).asList()
except pyparsing.ParseException as error:
    print error
    print pyparsing.line(error.loc, string)
except pyparsing.ParseSyntaxException as error:
    print error
    print pyparsing.line(error.loc, string)
    print (error.col - 1) * ' ' + '^'

