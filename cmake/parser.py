__author__ = 'tahsmith'

from cmake import grammar
from cmake.arguments.argument import *
from cmake.statements.command_invocation import CommandInvocation


class Parser(grammar.Grammar):
    def __init__(self):
        super(Parser, self).__init__()
        self.interpolation_fragment.setParseAction(StringFragment)
        self.quoted_argument.setParseAction(StringFragment)
        self.escaped_fragment.setParseAction(StringFragment)
        self.substitution_argument.setParseAction(InterpolatedString)
        self.variable_reference.setParseAction(VariableReference)
        self.generator_expression.setParseAction(VariableReference)
        self.env_variable_reference.setParseAction(EnvironmentVariableReference)
        self.argument_list.setParseAction(ArgumentList)
        self.command_invocation.setParseAction(CommandInvocation)