__author__ = 'tahsmith'

from pyparsing import *

space = Regex('[ \t]+')
newline = '\n'
open_bracket = Literal('(').suppress()
close_bracket = Literal(')').suppress()
if_keyword = CaselessKeyword('if').suppress()
endif_keyword = CaselessKeyword('endif').suppress()
elseif_keyword = CaselessKeyword('elseif').suppress()
else_keyword = CaselessKeyword('else').suppress()
set_keyword = CaselessKeyword('set').suppress()
macro_keyword = CaselessKeyword('macro').suppress()
endmacro_keyword = CaselessKeyword('endmacro').suppress()
keyword = (
    if_keyword |
    elseif_keyword |
    else_keyword |
    endif_keyword |
    set_keyword |
    macro_keyword |
    endmacro_keyword
)
identifier_chars = alphanums+"_-@"
identifier = (~keyword + Word(identifier_chars))("identifier")

interpolated_identifier = Forward()
string_variable_reference = Literal("{").suppress() + interpolated_identifier + Literal("}").suppress()
env_variable_reference = CaselessLiteral("env{").suppress() + interpolated_identifier + Literal("}").suppress()
begin_variable_reference = Literal("$").suppress()
variable_reference = (begin_variable_reference + (string_variable_reference | env_variable_reference))("variable_reference")
interpolated_identifier <<= OneOrMore(identifier | Group(variable_reference))

argument = identifier | variable_reference
argument_list = (open_bracket + Group(ZeroOrMore(argument)) + close_bracket)("argument_list")
nonempty_argument_list = open_bracket + OneOrMore(identifier) + close_bracket
placeholder_argument_list = (open_bracket + close_bracket).suppress()
command_invocation = (identifier + argument_list)("command_invocation")

statement = Forward()
predicate = nonempty_argument_list.copy()('predicate')
statement_list = ZeroOrMore(statement)("statement_list")

elseif_branch = (elseif_keyword + Group(Group(predicate) + Group(statement_list)))('else_if')
else_branch = (else_keyword + placeholder_argument_list + Group(statement_list))('else')
if_statement = (if_keyword + Group(Group(predicate) + Group(statement_list))('if') +
                ZeroOrMore(elseif_branch) +
                Optional(else_branch) +
                endif_keyword + argument_list.suppress())

set_statement = (set_keyword + open_bracket + argument + Group(ZeroOrMore(argument)) + close_bracket)('set')

statement <<= command_invocation | if_statement | set_statement

macro_definition = (macro_keyword + open_bracket + argument + Group(ZeroOrMore(argument)) + close_bracket +
                    Group(statement_list) +
                    endmacro_keyword + argument_list.suppress())

file_element = (
    statement
)

file = (ZeroOrMore(file_element) + StringEnd())('file')