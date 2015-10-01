from unittest import TestCase

from cmake.arguments.argument import *

__author__ = 'tahsmith'


class EvaluationContextBase(TestCase):
    ctx = Context()


class TestStringFragment(EvaluationContextBase):
    string_fragment = StringFragment(['x'])

    def test_evaluate(self):
        self.assertEqual(
            self.string_fragment.evaluate(self.ctx), 'x'
        )


class TestInterpolatedString(EvaluationContextBase):
    interpolated_string = InterpolatedString([StringFragment(['x']), StringFragment(['y'])])

    def test_evaluate(self):
        self.assertEqual(
            self.interpolated_string.evaluate(self.ctx), 'xy'
        )


class TestVariableReference(EvaluationContextBase):
    variable_reference = VariableReference([InterpolatedString([StringFragment(['x'])])])

    def test_evaluate(self):
        self.ctx.variable_stack[0]['x'] = 'value'
        self.assertEqual(
            self.variable_reference.evaluate(self.ctx),
            'value'
        )


class TestArgumentList(EvaluationContextBase):
    argument_list = ArgumentList([VariableReference([InterpolatedString([StringFragment(['var'])])]),
                                  StringFragment(['y;z'])])

    def test_evaluate(self):
        self.ctx.variable_stack[0]['var'] = 'x'
        self.assertEqual(
            self.argument_list.evaluate(self.ctx),
            ['x', 'y', 'z']
        )