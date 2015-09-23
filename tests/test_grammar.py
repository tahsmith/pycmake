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

    def test_identifier_fragment(self):
        self.assertExpression(
            self.grammar.identifier_fragment,
            "repos/cmake/Tests/Simple/CMakeLists.txt",
            ["repos/cmake/Tests/Simple/CMakeLists.txt"])
        self.assertExpression(
            self.grammar.identifier_fragment,
            "CMAKE_PREFIX_PATH",
            ["CMAKE_PREFIX_PATH"])

    def test_simple_string(self):
        self.assertExpression(
            self.grammar.interpolated_string,
            '"hello, world!"',
            ["hello, world!"])
        # Should be able to accept a string with a '$' without it being escaped
        self.assertExpression(
            self.grammar.interpolated_string,
            r'"cd $HOME"',
            [r'cd $HOME'])

    def test_escaped_string(self):
        self.assertExpression(
            self.grammar.interpolated_string,
            r'"hello, \"world!\""',
            [r'hello, \"world!\"'])
        self.assertExpression(
            self.grammar.interpolated_string,
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

    def test_interpolated_string(self):
        self.assertExpression(
            self.grammar.interpolated_string,
            r'"hello, \"${world}!\""',
            [r'hello, \"', 'world', r'!\"'])
        self.assertExpression(
            self.grammar.interpolated_string,
            r'"hello, \"${wo$ENV{r}ld}!\""',
            [r'hello, \"', 'wo', 'r', 'ld', r'!\"'])

    def test_command_invocation(self):
        self.assertExpression(self.grammar.command_invocation, "command()", ['command', []])
        self.assertExpression(self.grammar.command_invocation, "command(arg1 arg2)", ["command", ['arg1', 'arg2']])
        self.assertExpression(self.grammar.command_invocation, "command(arg ${var})", ["command", ['arg', 'var']])
        self.assertExpression(self.grammar.command_invocation, 'command(arg "hello, world!")',
                              ["command", ['arg', "hello, world!"]])
        self.assertExpression(self.grammar.command_invocation, 'command(arg ${var} "hello, world!")',
                              ["command", ['arg', 'var', 'hello, world!']])

    def test_if_statement(self):
        self.assertExpression(
            self.grammar.if_statement,
            '''
            if(NOT arg ${arg2} "hello, world")
                command(arg1 arg2)
            endif()
            ''',
            [[['NOT', 'arg', 'arg2', "hello, world"],
              ['command', ['arg1', 'arg2']]]]
        )

    def test_if_else_statement(self):
        self.assertExpression(
            self.grammar.if_statement,
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
            self.grammar.if_statement,
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
            self.grammar.set_statement,
            '''
            set(var)
            ''',
            ['var', []]
        )
        self.assertExpression(
            self.grammar.set_statement,
            '''
            set(var value)
            ''',
            ['var', ['value']]
        )
        self.assertExpression(
            self.grammar.set_statement,
            '''
            set(${var} ${value})
            ''',
            ['var', ['value']]
        )

    def test_macro(self):
        self.assertExpression(
            self.grammar.macro_definition,
            '''
            macro(name arg)

            endmacro()
            ''',
            ['name', ['arg'], []]
        )

        self.assertExpression(
            self.grammar.macro_definition,
            '''
            macro(name arg)
                command(arg )
            endmacro()
            ''',
            ['name', ['arg'], ['command',['arg']]]
        )

if __name__ == '__main__':
    unittest.main()
