__author__ = 'tahsmith'

from cmake import grammar
# from cmake.elements.variable import IdentifierFragment, InterpolatedIdentifier, VariableReference


class Parser(grammar.Grammar):
    def __init__(self):
        super(Parser, self).__init__()
        # self.variable_reference.setParseAction(VariableReference)
        # self.substitution_argument.setParseAction(InterpolatedIdentifier)
        # self.unquoted_argument.setParseAction(IdentifierFragment)