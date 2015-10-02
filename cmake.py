__author__ = 'tahsmith'

import sys
import argparse

import pyparsing
from cmake.parser import Parser
from cmake.context import Context
from cmake.functions.message import message
from cmake.functions.set import set

argparser = argparse.ArgumentParser()
group = argparser.add_mutually_exclusive_group()
group.add_argument("file", nargs='?', default=None)
group.add_argument("--interactive", action="store_true", help="read-evaluate-print loop mode")
args = argparser.parse_args()


def handle_error_and_exit(source, error):
    print 'Error parsing {}: {}'.format(source, error)
    print pyparsing.line(error.loc, string)
    print (error.col - 1) * ' ' + '^'
    sys.exit(1)


def setup_context():
    context = Context()
    context.callables['message'] = message
    context.callables['set'] = set
    return context

if __name__ == '__main__':
    parser = Parser()
    context = setup_context()
    context.variable_stack[0]['x'] = '1'
    context.variable_stack[0]['var'] = 'value'
    if args.interactive:
        while True:
            try:
                line = raw_input('>')
                parser.command_invocation.parseString(line)[0].evaluate(context)
            except KeyboardInterrupt:
                sys.exit(0)
    else:
        try:
            f = open(args.file)
        except IOError:
            sys.exit(1)
        string = f.read()

        try:
            parser.file.parseString(string).asList()
        except pyparsing.ParseException as error:
            handle_error_and_exit(args.file, error)
        except pyparsing.ParseSyntaxException as error:
            handle_error_and_exit(args.file, error)

