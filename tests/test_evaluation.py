from unittest import TestCase

from cmake.context import Context

__author__ = 'tahsmith'


class TestEvaluationContext(TestCase):
    ctx = Context()

    def test_variable_lookup(self):
        self.ctx.variable_stack[0]['x'] = 'x-value'
        self.assertEqual(
            self.ctx.variable_lookup('x'), 'x-value'
        )
        self.ctx.variable_stack.append({'x': 'x-value-new'})
        self.assertEqual(
            self.ctx.variable_lookup('x'), 'x-value-new'
        )
