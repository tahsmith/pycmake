from cmake.context import Context

__author__ = 'tahsmith'


class CommandInvocation(object):
    def __init__(self, tokens):
        self.command_name = tokens[0][0]
        self.argument_list = tokens[0][1][0]

    def evaluate(self, ctx):
        """

        :type ctx: Context
        """
        arg_list = self.argument_list.evaluate(ctx)
        ctx.callables[self.command_name](ctx, arg_list)