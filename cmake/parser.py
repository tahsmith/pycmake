__author__ = 'tahsmith'

from cmake import grammar
from variable import IdentifierFragment, InterpolatedIdentifier, VariableReference


class Parser(grammar.Grammar):
    def __init__(self):
        super(Parser, self).__init__()
        self.variable_reference.setParseAction(VariableReference)
        self.interpolated_identifier.setParseAction(InterpolatedIdentifier)
        self.identifier_fragment.setParseAction(IdentifierFragment)