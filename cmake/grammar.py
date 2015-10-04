from operator import or_
import re
from pyparsing import *
from functools import reduce

__author__ = 'tahsmith'


def charFrom(chars):
    return reduce(or_, (Literal(char) for char in chars))


def escapeChar(tokens):
    return ('\\' + tokens[0]).decode('string_escape')


class Grammar(object):
    def __init__(self):
        self.if_keyword = CaselessKeyword('if').suppress()
        self.endif_keyword = CaselessKeyword('endif').suppress()
        self.elseif_keyword = CaselessKeyword('elseif').suppress()
        self.else_keyword = CaselessKeyword('else').suppress()
        self.endmacro_keyword = CaselessKeyword('endmacro').suppress()
        self.macro_keyword = CaselessKeyword('macro').suppress()
        keyword = (
            self.if_keyword |
            self.elseif_keyword |
            self.else_keyword |
            self.endif_keyword |
            self.macro_keyword |
            self.endmacro_keyword
        )

        begin_interpolation = Literal("$").suppress()
        env_keyword = CaselessLiteral("env").suppress()
        left_curly = Literal("{").suppress()
        right_curly = Literal("}").suppress()
        left_bracket = Literal('(').suppress()
        right_bracket = Literal(')').suppress()
        left_angle = Literal("<").suppress()
        right_angle = Literal(">").suppress()
        start_of_interpolation = (begin_interpolation + Optional(env_keyword)) + (left_curly | left_angle)
        end_of_interpolation = right_angle | right_curly
        start_attrs = Literal(":").suppress()
        attr_separator = Literal(",").suppress()

        # Interpolation expressions
        self.substitution_argument = Forward()
        interpolation_atom = ~(start_of_interpolation |
                               end_of_interpolation |
                               start_attrs |
                               attr_separator) + Regex('[^ \t\n]')
        self.interpolation_fragment = Combine(OneOrMore(interpolation_atom))
        self.cmake_variable_reference = (left_curly +
                                         self.substitution_argument -
                                         right_curly)
        self.env_variable_reference = (env_keyword +
                                       left_curly -
                                       self.substitution_argument -
                                       right_curly)
        self.variable_reference = begin_interpolation + (self.cmake_variable_reference | self.env_variable_reference)

        # Generator expressions
        self.generator_expression = (begin_interpolation + left_angle -
                                     self.substitution_argument +
                                     Optional(start_attrs - delimitedList(self.substitution_argument)) -
                                     right_angle)
        substitution = self.variable_reference | self.generator_expression
        self.substitution_argument <<= OneOrMore(
            self.interpolation_fragment |
            substitution)

        # Unquoted argument
        unquoted_delimiter = charFrom(' "\t#();\\')
        unquoted_atom = ~unquoted_delimiter + Regex('.')
        escape_char = Literal('\\').suppress()
        unquoted_escape_identity = escape_char + charFrom('()#" \t\\$@^;')
        escape_encoded = escape_char - charFrom('ntr').setParseAction(escapeChar)
        unquoted_escape_sequence = (
            unquoted_escape_identity |
            escape_encoded
        )
        unquoted_fragment = Combine(OneOrMore(unquoted_atom | unquoted_escape_sequence))
        self.escaped_fragment = Combine(OneOrMore(~start_of_interpolation + Regex('.')))

        def divideUnquoted(s, l, t):
            return OneOrMore(self.escaped_fragment |
                             substitution).parseString(t[0], parseAll=True)

        self.unquoted_argument = unquoted_fragment.copy()
        self.unquoted_argument.setParseAction(divideUnquoted)

        # Quoted argument
        quoted_delimiter = start_of_interpolation
        quoted_atom = ~quoted_delimiter + Regex('.', re.DOTALL)
        quoted_escape_identity = escape_char + charFrom(';')
        quoted_escape_sequence = (
            escape_encoded |
            quoted_escape_identity
        )
        quoted_fragment = Combine(OneOrMore(quoted_atom | quoted_escape_sequence))
        quoted_argument_inner = ZeroOrMore(quoted_fragment | substitution)
        self.quoted_argument = QuotedString('"', '\\', multiline=True)

        def parseInner(s, l, t):
            return quoted_argument_inner.parseString(t[0], True)

        self.quoted_argument.setParseAction(
            parseInner
        )

        # Block argument
        def parseBlock(s, l, t):
            return t.c

        self.block_argument = Regex(r'\[(?P<e>[=]*)\[(?P<c>.*?)\](?P=e)\]', flags=re.DOTALL)
        self.block_argument.setParseAction(parseBlock)

        argument_separation = Literal(';').suppress()
        self.argument = (
            self.block_argument |
            self.quoted_argument |
            self.unquoted_argument |
            argument_separation
        )
        argument_list = Forward()
        argument_list <<= ZeroOrMore(Group(left_bracket - argument_list - right_bracket) | self.argument)
        self.argument_list = argument_list
        placeholder_brackets = (left_bracket - argument_list.suppress() - right_bracket).suppress()
        command_identifier = Word(alphanums + '_-')
        self.command_invocation = ~keyword + Group(
            command_identifier - left_bracket - Group(argument_list) - right_bracket)

        self.statement = Forward()
        self.statement_list = ZeroOrMore(self.statement)
        logic_argument_list = left_bracket - argument_list - right_bracket
        elseif_branch = self.elseif_keyword - Group(Group(logic_argument_list) - Group(self.statement_list))
        else_branch = self.else_keyword - placeholder_brackets - Group(self.statement_list)

        self.if_statement = (
            self.if_keyword - Group(Group(logic_argument_list) - Group(self.statement_list)) -
            ZeroOrMore(elseif_branch) -
            Optional(else_branch) -
            self.endif_keyword - left_bracket - right_bracket)

        self.statement <<= (
            self.command_invocation |
            self.if_statement
        )

        self.macro_definition = (self.macro_keyword - left_bracket -
                                 Group(OneOrMore(self.argument)) -
                                 right_bracket -
                                 Group(self.statement_list) -
                                 self.endmacro_keyword - placeholder_brackets)

        self.file_element = (
            self.statement |
            self.macro_definition
        )
        self.file = (ZeroOrMore(self.file_element) + StringEnd())('file')

        self.block_comment = '#' + self.block_argument
        self.line_comment = '#' + restOfLine
        self.comment = self.block_comment | self.line_comment
        self.file.ignore(self.comment)
