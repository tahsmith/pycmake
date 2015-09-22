__author__ = 'tahsmith'

import grammar
from variable import Identifier, InterpolatedIdentifier, VariableReference

grammar.variable_reference.setParseAction(VariableReference)
grammar.interpolated_identifier.setParseAction(InterpolatedIdentifier)
grammar.identifier.setParseAction(Identifier)

variable_reference = grammar.variable_reference.copy()