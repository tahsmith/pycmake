__author__ = 'tahsmith'


def set(context, argument_list):
    context.variable_stack[0][argument_list[0]] = argument_list[1]