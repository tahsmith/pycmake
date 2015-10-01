__author__ = 'tahsmith'

from cmake import grammar
from cmake.elements.argument import VariableReference, InterpolatedString, StringFragment


class Parser(grammar.Grammar):
    def __init__(self):
        super(Parser, self).__init__()
        self.interpolation_fragment.setParseAction(StringFragment)
        self.substitution_argument.setParseAction(InterpolatedString)
        self.variable_reference.setParseAction(VariableReference)
