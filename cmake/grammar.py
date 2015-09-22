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
        self.identifier_chars = alphanums + "_-@"

        self.interpolated_identifier = Forward()
        begin_variable_reference = Literal("$").suppress()
        self.string_variable_reference = nestedExpr("{", "}", content=self.interpolated_identifier)
        self.env_variable_reference = nestedExpr(CaselessLiteral("env{"), "}", content=self.interpolated_identifier)
        self.identifier_fragment = (~keyword + Word(self.identifier_chars))("identifier")
        self.variable_reference = (begin_variable_reference + (self.string_variable_reference | self.env_variable_reference))(
            "variable_reference")
        self.interpolated_identifier <<= OneOrMore(self.identifier_fragment | Group(self.variable_reference))

        argument = self.identifier_fragment | self.variable_reference
        open_bracket = Literal('(').suppress()
        close_bracket = Literal(')').suppress()
        argument_list = (open_bracket + Group(ZeroOrMore(argument)) + close_bracket)("argument_list")
        nonempty_argument_list = open_bracket + OneOrMore(self.identifier_fragment) + close_bracket
        placeholder_argument_list = (open_bracket + close_bracket).suppress()

        predicate = nonempty_argument_list.copy()('predicate')
        self.statement = Forward()

        self.statement_list = ZeroOrMore(self.statement)("statement_list")
        elseif_branch = (self.elseif_keyword + Group(Group(predicate) + Group(self.statement_list)))('else_if')
        else_branch = (self.else_keyword + placeholder_argument_list + Group(self.statement_list))('else')

        self.if_statement = (
            self.if_keyword + Group(Group(predicate) + Group(self.statement_list))('if') + ZeroOrMore(elseif_branch) +
            Optional(else_branch) + self.endif_keyword + argument_list.suppress())
        self.command_invocation = (self.identifier_fragment + argument_list)("command_invocation")
        self.set_statement = (self.set_keyword + open_bracket + argument + Group(ZeroOrMore(argument)) + close_bracket)('set')
        self.statement <<= self.command_invocation | self.if_statement | self.set_statement

        self.macro_definition = (self.macro_keyword + open_bracket + argument +
                                 Group(ZeroOrMore(argument)) + close_bracket +
                                 Group(self.statement_list) + self.endmacro_keyword + argument_list.suppress())

        self.file_element = self.statement
        self.file = (ZeroOrMore(self.file_element) + StringEnd())('file')