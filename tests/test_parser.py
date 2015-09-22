__author__ = 'tahsmith'

from unittest import TestCase
from cmake.parser import Parser

class TestParser(TestCase):
    parser = Parser()
    def test_identifier(self):
        self.assertEqual(
            self.parser.identifier_fragment.parseString("var")[0].interpolate({}),
            'var'
        )

    def test_interpolatedidentifier(self):
        self.assertEqual(
            self.parser.interpolated_identifier.parseString("var")[0].interpolate({}),
            'var')

    # def test_variable(self):
    #     self.assertEqual(
    #         self.parser.variable_reference.parseString("${var}")[0].interpolate({'var': 'value'}),
    #         'value'
    #     )