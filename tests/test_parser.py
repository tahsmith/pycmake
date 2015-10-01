__author__ = 'tahsmith'

from unittest import TestCase

from cmake.parser import Parser
from cmake.context import Context


class TestParser(TestCase):
    ctx = Context()
    parser = Parser()

    # def test_identifier(self):
    #     self.assertEqual(
    #         self.parser.unquoted_argument.parseString("var")[0].interpolate({}),
    #         'var'
    #     )

    # def test_interpolatedidentifier(self):
    #     self.assertEqual(
    #         self.parser.substitution_argument.parseString("var")[0].interpolate({}),
    #         'var')

    def test_variable(self):
        self.ctx.variable_stack[0]['var0'] = 'value'
        self.ctx.variable_stack[0]['N'] = '0'
        self.assertEqual(
            self.parser.variable_reference.parseString("${var0}")[0].evaluate(self.ctx),
            'value')
        self.assertEqual(
            self.parser.variable_reference.parseString("${var${N}}")[0].evaluate(self.ctx),
            'value')