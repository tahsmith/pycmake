__author__ = 'tahsmith'

from pyparsing import *


class Grammar(object):
    def __init__(self):
        self.if_keyword = CaselessKeyword('if').suppress()
        self.endif_keyword = CaselessKeyword('endif').suppress()
        self.elseif_keyword = CaselessKeyword('elseif').suppress()
        self.else_keyword = CaselessKeyword('else').suppress()
        self.set_keyword = CaselessKeyword('set').suppress()
        self.endmacro_keyword = CaselessKeyword('endmacro').suppress()
        self.macro_keyword = CaselessKeyword('macro').suppress()
        keyword = (
            self.if_keyword |
            self.elseif_keyword |
            self.else_keyword |
            self.endif_keyword |
            self.set_keyword |
            self.macro_keyword |
            self.endmacro_keyword
        )
        self.identifier_chars = alphanums + "./:_-@"

        self.interpolated_identifier = Forward()
        begin_variable_reference = Literal("$").suppress()
        left_curly = Literal("{").suppress()
        right_curly = Literal("}").suppress()
        self.string_variable_reference = left_curly - self.interpolated_identifier - right_curly
        self.env_variable_reference = (CaselessLiteral("env").suppress() - left_curly -
                                       self.interpolated_identifier - right_curly)
        self.identifier_fragment = ~keyword + Word(self.identifier_chars)
        self.variable_reference = (begin_variable_reference -
                                   (self.string_variable_reference | self.env_variable_reference))

        self.interpolated_identifier <<= OneOrMore(self.identifier_fragment | self.variable_reference)

        quote = Literal('"').suppress()
        self.string_fragment = Combine(OneOrMore(CharsNotIn(r'"$\\') | (Literal('\\').suppress() - '"')))
        self.interpolated_string = (quote +
                                    ZeroOrMore(self.string_fragment | self.variable_reference) +
                                    quote)

        open_bracket = Literal('(').suppress()
        close_bracket = Literal(')').suppress()
        self.argument = self.identifier_fragment | self.variable_reference | self.interpolated_string
        argument_list = open_bracket - Group(ZeroOrMore(self.argument)) - close_bracket
        nonempty_argument_list = open_bracket - Group(OneOrMore(self.argument)) - close_bracket
        placeholder_argument_list = (open_bracket - close_bracket).suppress()
        self.statement = Forward()

        self.statement_list = ZeroOrMore(self.statement)("statement_list")
        elseif_branch = self.elseif_keyword - Group(nonempty_argument_list - Group(self.statement_list))
        else_branch = self.else_keyword - placeholder_argument_list - Group(self.statement_list)

        self.if_statement = (
            self.if_keyword - Group(nonempty_argument_list - Group(self.statement_list)) -
            ZeroOrMore(elseif_branch) -
            Optional(else_branch) -
            self.endif_keyword - argument_list.suppress())
        self.command_invocation = self.identifier_fragment - argument_list
        self.set_statement = (self.set_keyword - open_bracket -
                              self.argument - Group(ZeroOrMore(self.argument)) -
                              close_bracket)
        self.statement <<= self.command_invocation | self.if_statement | self.set_statement

        self.macro_definition = (self.macro_keyword - open_bracket - self.argument -
                                 Group(ZeroOrMore(self.argument)) - close_bracket -
                                 Group(self.statement_list) - self.endmacro_keyword - argument_list.suppress())

        self.file_element = (
            self.statement |
            self.macro_definition
        )
        self.file = (ZeroOrMore(self.file_element) + StringEnd())('file')

        self.comment = '#' + restOfLine
        self.file.ignore(self.comment)