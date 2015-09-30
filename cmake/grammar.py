__author__ = 'tahsmith'

from pyparsing import *
from operator import or_
from itertools import chain
import re


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
        self.set_keyword = CaselessKeyword('set').suppress()
        self.unset_keyword = CaselessKeyword('unset').suppress()
        self.endmacro_keyword = CaselessKeyword('endmacro').suppress()
        self.macro_keyword = CaselessKeyword('macro').suppress()
        keyword = (
            self.if_keyword |
            self.elseif_keyword |
            self.else_keyword |
            self.endif_keyword |
            self.set_keyword |
            self.unset_keyword |
            self.macro_keyword |
            self.endmacro_keyword
        )

        begin_interpolation = Literal("$").suppress()
        env_keyword = CaselessLiteral("env").suppress()
        left_curly = Literal("{").suppress()
        right_curly = Literal("}").suppress()
        left_bracket = Literal("(").suppress()
        right_bracket = Literal(")").suppress()
        left_angle = Literal("<").suppress()
        right_angle = Literal(">").suppress()
        quote = Literal('"').suppress()
        start_of_interpolation = (begin_interpolation + Optional(env_keyword)) + (left_curly | left_angle)
        end_of_interpolation = right_angle | right_curly
        start_attrs = Literal(":").suppress()
        attr_separator = Literal(",").suppress()

        ## Interpolation expressions
        self.interpolated_expression = Forward()
        interpolation_atom = ~(start_of_interpolation |
                               end_of_interpolation |
                               start_attrs |
                               attr_separator) + Regex('.')
        interpolation_fragment = Combine(OneOrMore(interpolation_atom))
        self.cmake_variable_reference = (left_curly +
                                          self.interpolated_expression -
                                          right_curly)
        self.env_variable_reference = (env_keyword +
                                       left_curly -
                                       self.interpolated_expression -
                                       right_curly)
        self.variable_reference = begin_interpolation + (self.cmake_variable_reference | self.env_variable_reference)
        # Generator expressions
        self.generator_expression = (begin_interpolation + left_angle -
                                     self.interpolated_expression +
                                     Optional(start_attrs - delimitedList(self.interpolated_expression)) -
                                     right_angle)
        substitution = self.variable_reference | self.generator_expression
        self.interpolated_expression <<= OneOrMore(
            interpolation_fragment |
            substitution)

        ## Unquoted identifier
        unquoted_delimiter = charFrom(' "\t#()\\;') | start_of_interpolation
        unquoted_atom = ~unquoted_delimiter + Regex('.')
        escape_char = Literal('\\').suppress()
        unquoted_escape_identity = escape_char + charFrom('()#" \t\\$@^')
        unquoted_escape_encoded = escape_char + charFrom('ntr').setParseAction(escapeChar)
        unquoted_escape_sequence = (
            unquoted_escape_identity |
            unquoted_escape_encoded
        )
        unquoted_fragment = Combine(OneOrMore(unquoted_atom | unquoted_escape_sequence))
        self.unquoted_argument = OneOrMore(unquoted_fragment |
                                           substitution)

        quoted_delimiter = start_of_interpolation
        quoted_atom = ~quoted_delimiter + Regex('.', re.DOTALL)
        quoted_escape_encoded = escape_char + charFrom('ntr').setParseAction(escapeChar)
        quoted_escape_sequence = (
            quoted_escape_encoded
        )
        quoted_fragment = Combine(OneOrMore(quoted_atom | quoted_escape_sequence))
        quoted_argument_inner = ZeroOrMore(quoted_fragment | substitution)
        self.quoted_argument = QuotedString('"', '\\', multiline=True)
        self.quoted_argument.setParseAction(
            lambda s, l, t: quoted_argument_inner.parseString(t[0], True)
        )

        open_bracket = Literal('(').suppress()
        close_bracket = Literal(')').suppress()
        self.argument = (
            self.quoted_argument |
            self.unquoted_argument)
        argument_list = open_bracket - Group(ZeroOrMore(self.argument)) - close_bracket
        placeholder_argument_list = (open_bracket - close_bracket).suppress()
        command_identifier = Word(alphanums+'_-')
        self.command_invocation = ~keyword + command_identifier - argument_list

        # Logic
        unary_ops = ('EXISTS', )
        unary_kws = [Keyword(op) for op in unary_ops]
        binary_ops = ('GREATER', 'LESS')
        binary_kws = [Keyword(op) for op in binary_ops]
        not_kw = Keyword('NOT')
        boolean_ops = ('AND', 'OR')
        boolean_kws = [Keyword(op) for op in boolean_ops]
        logic_expression = Forward()
        logic_argument = (
            (~reduce(or_, chain(unary_kws, binary_kws, boolean_kws, (not_kw,))) + self.argument) |
            (left_bracket - Group(logic_expression) - right_bracket)
        )("logical_argument")
        unary_op = Group(reduce(or_, unary_kws) - logic_argument)("unary_op")
        binary_argument = logic_argument | unary_op
        binary_op = Group(binary_argument + reduce(or_, binary_kws) - binary_argument)('binary_op')
        boolean_argument = (binary_op | unary_op | logic_argument)
        not_op = Group(not_kw - boolean_argument)
        boolean_op = Group(boolean_argument + reduce(or_, boolean_kws) - boolean_argument)
        logic_expression <<= (
            boolean_op |
            not_op |
            binary_op |
            unary_op |
            logic_argument
            )
        self.logical_expression = logic_expression
        logic_argument_list = open_bracket - Group(logic_expression) - close_bracket

        self.statement = Forward()
        self.statement_list = ZeroOrMore(self.statement)
        elseif_branch = self.elseif_keyword - Group(logic_argument_list - Group(self.statement_list))
        else_branch = self.else_keyword - placeholder_argument_list - Group(self.statement_list)

        self.if_statement = (
            self.if_keyword - Group(logic_argument_list - Group(self.statement_list)) -
            ZeroOrMore(elseif_branch) -
            Optional(else_branch) -
            self.endif_keyword - argument_list.suppress())

        self.set_statement = (self.set_keyword - open_bracket -
                              Group(OneOrMore(self.argument)) -
                              close_bracket)
        self.unset_statement = (self.unset_keyword - open_bracket -
                                Group(OneOrMore(self.argument)) -
                                close_bracket)

        self.statement <<= (
            self.command_invocation |
            self.if_statement |
            self.set_statement |
            self.unset_statement
        )

        self.macro_definition = (self.macro_keyword - open_bracket -
                                 Group(OneOrMore(self.argument)) -
                                 close_bracket -
                                 Group(self.statement_list) -
                                 self.endmacro_keyword - argument_list.suppress())

        self.file_element = (
            self.statement |
            self.macro_definition
        )
        self.file = (ZeroOrMore(self.file_element) + StringEnd())('file')

        self.comment = '#' + restOfLine
        self.file.ignore(self.comment)

    def substitute(self, s, l, t):
        return self.interpolated_expression.parseString(t[0], True)