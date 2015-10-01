from cmake.context import Context

__author__ = 'tahsmith'


class CommandInvocation(object):
    def __init__(self, tokens):
        self.command_name = tokens[0]
        self.argument_list = tokens[1]

    def invoke(self, ctx):
        """

        :type ctx: Context
        """
        ctx.callables[self.command_name].invoke(ctx, self.argument_list.evaluate(ctx))