__author__ = 'tahsmith'

import unittest

import pyparsing
from cmake.grammar import Grammar


class TestGrammar(unittest.TestCase):
    grammar = Grammar()

    def assertExpression(self, rule, string, expected):
        self.assertEqual((rule + pyparsing.stringEnd).parseString(string).asList(),
                         expected)

    def test_comment(self):
        self.assertExpression(
            self.grammar.file,
            "# Not parsed, if endif set macro",
            []
        )

    def test_simple_unquoted(self):
        self.assertExpression(
            self.grammar.unquoted_argument,
            "repos/cmake/Tests/Simple/CMakeLists.txt",
            ["repos/cmake/Tests/Simple/CMakeLists.txt"])
        self.assertExpression(
            self.grammar.unquoted_argument,
            "CMAKE_PREFIX_PATH",
            ["CMAKE_PREFIX_PATH"])
        # These are the characters that appear in thins like paths, command args, etc.
        self.assertExpression(
            self.grammar.unquoted_argument,
            r"[]./:_-@*+<>=",
            [r"[]./:_-@*+<>="])

    def test_simple_quoted(self):
        self.assertExpression(
            self.grammar.quoted_argument,
            '"hello, world!"',
            ["hello, world!"])
        # Should be able to accept a string with a '$' without it being escaped
        self.assertExpression(
            self.grammar.quoted_argument,
            r'"cd $HOME"',
            [r'cd $HOME'])
        self.assertExpression(
            self.grammar.quoted_argument,
            '"x\ny"',
            ['x\ny']
        )

    def test_escaped_quoted(self):
        self.assertExpression(
            self.grammar.quoted_argument,
            r'"hello, \"world!\""',
            [r'hello, "world!"'])
        self.assertExpression(
            self.grammar.quoted_argument,
            r'"\\\;\n"',
            [r'\\\;\n'])

    def test_string_variable(self):
        self.assertExpression(self.grammar.variable_reference, "${var}", ["var"])
        self.assertExpression(self.grammar.variable_reference, "${${var}}", ["var"])
        self.assertExpression(self.grammar.variable_reference, "${${var}${var}}", ["var", 'var'])
        self.assertExpression(self.grammar.variable_reference, "${var${var}var}", ['var', "var", 'var'])
        self.assertExpression(self.grammar.variable_reference, "${var$ENV{v${a}r}var}", ['var', "v", "a", "r", 'var'])

    def test_env_variable(self):
        self.assertExpression(self.grammar.variable_reference, "$ENV{var}", ["var"])

    def test_generator_expression(self):
        self.assertExpression(self.grammar.generator_expression, "$<x>", ['x'])
        self.assertExpression(self.grammar.generator_expression, "$<$<x>>", ['x'])
        self.assertExpression(self.grammar.generator_expression, "$<$<x>:$<x>,$<x>>", ['x', 'x', 'x'])

    def test_interpolated_string(self):
        self.assertExpression(
            self.grammar.quoted_argument,
            r'"${x}"',
            ['x']
        )
        self.assertExpression(
            self.grammar.quoted_argument,
            r'"hello, \"${world}!\""',
            [r'hello, "', 'world', r'!"'])
        self.assertExpression(
            self.grammar.quoted_argument,
            r'"hello, \"${wo$ENV{r}ld}!\""',
            [r'hello, "', 'wo', 'r', 'ld', r'!"'])

    def test_command_invocation(self):
        self.assertExpression(self.grammar.command_invocation, "command()", ['command', []])
        self.assertExpression(self.grammar.command_invocation, "command(arg1 arg2)", ["command", ['arg1', 'arg2']])
        self.assertExpression(self.grammar.command_invocation, "command(arg ${var})", ["command", ['arg', 'var']])
        self.assertExpression(self.grammar.command_invocation, "command(arg $<var>)", ["command", ['arg', 'var']])
        self.assertExpression(self.grammar.command_invocation, 'command(arg "hello, world!")',
                              ["command", ['arg', "hello, world!"]])
        self.assertExpression(self.grammar.command_invocation, 'command(arg ${var} $<var> "hello, world!")',
                              ["command", ['arg', 'var', 'var', 'hello, world!']])
        self.assertExpression(self.grammar.command_invocation, "command(SET IF MACRO FUNCTION)",
                              ['command', ['SET', 'IF', 'MACRO', 'FUNCTION']])

    def test_unary_logical_expression(self):
        self.assertExpression(
            self.grammar.logical_expression,
            'NOT x',
            ['NOT', 'x']
        )

    def test_binary_logical_expression(self):
        self.assertExpression(
            self.grammar.logical_expression,
            'x AND y',
            ['x', 'AND', 'y']
        )

    def test_grouped_logical_expression(self):
        self.assertExpression(
            self.grammar.logical_expression,
            'x GREATER y AND NOT z',
            [['x', 'GREATER', 'y'], 'AND', ['NOT', 'z']]
        )

    # def test_if_statement(self):
    #     self.assertExpression(
    #         self.grammar.if_statement,
    #         '''
    #         if(NOT arg AND ${arg2} AND "hello, world")
    #             command(arg1 arg2)
    #         endif()
    #         ''',
    #         [[['NOT', 'arg', 'arg2', "hello, world"],
    #           ['command', ['arg1', 'arg2']]]]
    #     )
    #
    # def test_if_else_statement(self):
    #     self.assertExpression(
    #         self.grammar.if_statement,
    #         '''
    #         if(NOT arg)
    #             command(arg1 arg2)
    #         else()
    #             command2(arg1 arg2)
    #         endif()
    #         ''',
    #         [[['NOT', 'arg'],
    #           ['command', ['arg1', 'arg2']]],
    #          ['command2', ['arg1', 'arg2']]]
    #     )
    #
    # def test_if_elseif_else_statement(self):
    #     self.assertExpression(
    #         self.grammar.if_statement,
    #         '''
    #         if(NOT arg)
    #             command(arg1 arg2)
    #         elseif(NOT arg2)
    #             command2(arg1 arg2)
    #         else()
    #             command3(arg1 arg2)
    #         endif()
    #         ''',
    #         [[['NOT', 'arg'],
    #           ['command', ['arg1', 'arg2']]],
    #          [['NOT', 'arg2'],
    #           ['command2', ['arg1', 'arg2']]],
    #          ['command3', ['arg1', 'arg2']]]
    #     )

    def test_set(self):
        self.assertExpression(
            self.grammar.set_statement,
            '''
            set(var)
            ''',
            [['var']]
        )
        self.assertExpression(
            self.grammar.set_statement,
            '''
            set(var value)
            ''',
            [['var', 'value']]
        )
        self.assertExpression(
            self.grammar.set_statement,
            '''
            set(${var} ${value})
            ''',
            [['var', 'value']]
        )
        self.assertExpression(
            self.grammar.set_statement,
            '''
            set(ENV{var} ${value})
            ''',
            [['ENV{var}', 'value']]
        )
        self.assertExpression(
            self.grammar.set_statement,
            r'''
            set("var" "value")
            ''',
            [['var', 'value']]
        )

    def test_unset(self):
        self.assertExpression(
            self.grammar.unset_statement,
            '''
            unset(var)
            ''',
            [['var']]
        )
        self.assertExpression(
            self.grammar.unset_statement,
            '''
            unset(ENV{var})
            ''',
            [['ENV{var}']]
        )

    def test_macro(self):
        self.assertExpression(
            self.grammar.macro_definition,
            '''
            macro(name arg)
                command(arg)
            endmacro()
            ''',
            [['name', 'arg'], ['command',['arg']]]
        )

if __name__ == '__main__':
    unittest.main()
