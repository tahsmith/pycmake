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
keyword = (
    if_keyword |
    elseif_keyword |
    else_keyword |
    endif_keyword
)
identifier = (~keyword + Word(alphas, alphanums))("identifier")

argument_list = (open_bracket + Group(ZeroOrMore(identifier)) + close_bracket)("argument_list")
nonempty_argument_list = open_bracket + OneOrMore(identifier) + close_bracket
placeholder_argument_list = (open_bracket + close_bracket).suppress()
command_invocation = Group(identifier + argument_list)("command_invocation")

statement = Forward()
predicate = nonempty_argument_list.copy()('predicate')
statement_list = ZeroOrMore(statement)("statement_list")

elseif_branch = (elseif_keyword + Group(predicate + Group(statement_list)))('else_if')
else_branch = (else_keyword + placeholder_argument_list + Group(statement_list))('else')
if_statement = (if_keyword + Group(predicate + Group(statement_list))('if') +
                ZeroOrMore(elseif_branch) +
                Optional(else_branch) +
                endif_keyword + argument_list.suppress())

statement <<= command_invocation | if_statement

file_element = (
    statement
)

file = (ZeroOrMore(file_element) + StringEnd())('file')