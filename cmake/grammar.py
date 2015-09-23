__author__ = 'tahsmith'

from pyparsing import *


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

        self.identifier_chars = alphanums + r"#;[]./_-@*+="
        self.interpolated_identifier = Forward()
        begin_interpolation = Literal("$").suppress()
        env_keyword = CaselessLiteral("env").suppress()
        left_curly = Literal("{").suppress()
        right_curly = Literal("}").suppress()
        left_bracket = Literal("(").suppress()
        right_bracket = Literal(")").suppress()
        left_angle = Literal("<").suppress()
        right_angle = Literal(">").suppress()
        quote = Literal('"').suppress()
        start_of_interpolation = (begin_interpolation + Optional(env_keyword)) - left_curly

        self.string_variable_reference = (left_curly -
                                          self.interpolated_identifier -
                                          right_curly)
        self.env_variable_reference = (env_keyword -
                                       left_curly -
                                       self.interpolated_identifier -
                                       right_curly)
        self.identifier_fragment = Word(self.identifier_chars)
        self.variable_reference = begin_interpolation + (self.string_variable_reference | self.env_variable_reference)

        # Generator expressions
        start_attrs = Literal(":").suppress()
        self.generator_expression = (begin_interpolation + left_angle -
                                     self.interpolated_identifier +
                                     Optional(start_attrs - delimitedList(self.interpolated_identifier)) -
                                     right_angle)

        self.interpolated_identifier <<= OneOrMore(
            self.identifier_fragment |
            self.variable_reference |
            self.generator_expression)

        string_elem = OneOrMore(~(quote | start_of_interpolation) +
                                (Optional('\\') + Regex('.')))
        self.string_fragment = Combine(OneOrMore(string_elem))
        self.interpolated_string = (quote +
                                    ZeroOrMore(self.string_fragment | self.variable_reference) +
                                    quote)

        open_bracket = Literal('(').suppress()
        close_bracket = Literal(')').suppress()
        self.argument = (
            self.identifier_fragment |
            self.variable_reference |
            self.generator_expression |
            self.interpolated_string)
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
        self.command_invocation = ~keyword + self.identifier_fragment - argument_list
        self.set_statement = (self.set_keyword - open_bracket -
                              (self.variable_reference | self.env_variable_reference | self.identifier_fragment) -
                              Group(ZeroOrMore(self.argument)) -
                              close_bracket)
        self.unset_statement = (self.unset_keyword - open_bracket -
                              (self.variable_reference | self.env_variable_reference | self.identifier_fragment) -
                              close_bracket)

        self.statement <<= (
            self.command_invocation |
            self.if_statement |
            self.set_statement |
            self.unset_statement
        )

        self.macro_definition = (self.macro_keyword - open_bracket -
                                 self.argument -
                                 Group(ZeroOrMore(self.argument)) -
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