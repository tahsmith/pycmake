from unittest import TestCase

__author__ = 'tahsmith'

from cmake.variable import VariableReference, InterpolatedIdentifier, IdentifierFragment


class TestIdentifier(TestCase):
    def test_interpolate(self):
        var = IdentifierFragment(['str'])
        self.assertEqual(var.interpolate({}), 'str')


class TestInterpolatedIdentifier(TestCase):
    def test_interpolate(self):
        var = InterpolatedIdentifier([IdentifierFragment(['var']), IdentifierFragment(['N'])])
        self.assertEqual(var.interpolate({}), 'varN')


class TestVariableReference(TestCase):
    def test_interpolate(self):
        var = VariableReference([InterpolatedIdentifier([IdentifierFragment(['va']), IdentifierFragment(['r'])])])
        self.assertEqual(
            var.interpolate({'var': 'value'}),
            'value')

        var = VariableReference([
            InterpolatedIdentifier([
                IdentifierFragment(['va']),
                VariableReference([
                     InterpolatedIdentifier([
                         IdentifierFragment(['r'])])])])])
        self.assertEqual(
            var.interpolate({'var': 'value', 'r': 'r'}),
            'value')
