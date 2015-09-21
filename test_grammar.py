__author__ = 'tahsmith'

import unittest

from grammar import *

class Grammar(unittest.TestCase):
    def assertExpression(self, rule, string, expected):
        self.assertEqual(rule.parseString(string).asList(),
                         expected)

    def test_string_variable(self):
        self.assertExpression(variable_reference, "${var}", ["var"])
        self.assertExpression(variable_reference, "${${var}}", ["var"])

    def test_env_variable(self):
        self.assertExpression(variable_reference, "$ENV{var}", ["var"])

    def test_command_invocation(self):
        self.assertExpression(command_invocation, "command()", ['command', []])
        self.assertExpression(command_invocation, "command(arg1 arg2)", ["command", ['arg1', 'arg2']])
        self.assertExpression(command_invocation, "command(arg ${var})", ["command", ['arg', 'var']])

    def test_if_statement(self):
        self.assertExpression(
            if_statement,
            '''
            if(NOT arg)
                command(arg1 arg2)
            endif()
            ''',
            [[['NOT', 'arg'],
              ['command', ['arg1', 'arg2']]]]
        )

    def test_if_else_statement(self):
        self.assertExpression(
            if_statement,
            '''
            if(NOT arg)
                command(arg1 arg2)
            else()
                command2(arg1 arg2)
            endif()
            ''',
            [[['NOT', 'arg'],
              ['command', ['arg1', 'arg2']]],
             ['command2', ['arg1', 'arg2']]]
        )

    def test_if_elseif_else_statement(self):
        self.assertExpression(
            if_statement,
            '''
            if(NOT arg)
                command(arg1 arg2)
            elseif(NOT arg2)
                command2(arg1 arg2)
            else()
                command3(arg1 arg2)
            endif()
            ''',
            [[['NOT', 'arg'],
              ['command', ['arg1', 'arg2']]],
             [['NOT', 'arg2'],
              ['command2', ['arg1', 'arg2']]],
             ['command3', ['arg1', 'arg2']]]
        )

    def test_set(self):
        self.assertExpression(
            set_statement,
            '''
            set(var)
            ''',
            ['var', []]
        )
        self.assertExpression(
            set_statement,
            '''
            set(var value)
            ''',
            ['var', ['value']]
        )
        self.assertExpression(
            set_statement,
            '''
            set(${var} ${value})
            ''',
            ['var', ['value']]
        )


if __name__ == '__main__':
    unittest.main()
