from unittest import TestCase

__author__ = 'tahsmith'

from cmake.elements.variable import VariableReference, InterpolatedIdentifier, IdentifierFragment
from cmake.elements.string import String, StringFragment


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


class TestString(TestCase):
    def test_interpolate(self):
        var = String([StringFragment(['hello, world!'])])
        self.assertEqual(
            var.interpolate({}),
            'hello, world!'
        )

    def test_interpolate(self):
        var = String([
            StringFragment(['hello, ']),
            VariableReference([InterpolatedIdentifier([IdentifierFragment(['name'])])]),
            StringFragment(['!'])
        ])
        self.assertEqual(
            var.interpolate({'name': 'world'}),
            'hello, world!'
        )
