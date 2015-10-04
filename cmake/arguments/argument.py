__author__ = 'tahsmith'

from operator import add
import os

from cmake.context import Context
from functools import reduce


class VariableReference(object):
    def __init__(self, tokens):
        self.name = tokens[0]

    def evaluate(self, ctx):
        """
        Perform any nested interpolations and give the value of the variable, or None.
        :type ctx: Context
        """
        return ctx.variable_lookup(self.name.evaluate(ctx))


class EnvironmentVariableReference(object):
    def __init__(self, tokens):
        self.name = tokens

    def evaluate(self, ctx):
        """
        Perform any nested interpolations and give the value of the variable, or None.
        :type ctx: Context
        """
        name = self.name.evaluate(ctx)
        if name in os.environ:
            return os.environ[name]
        else:
            return


class StringFragment(object):
    def __init__(self, tokens):
        self.token = tokens[0]

    def evaluate(self, ctx):
        return self.token


class InterpolatedString(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def evaluate(self, ctx):
        """
        Perform any substitutions in each token and join into one string.
        :type ctx: Context
        """
        return reduce(add, (token.evaluate(ctx) for token in self.tokens))


class ArgumentList(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def evaluate(self, ctx):
        """
        Process the argument tokens, performing interpolations and splitting semi-colon delimited lists.
        :param ctx: map of variables for performing substitutions.
        :return: list of strings
        """
        # Interpolate tokens.
        list = (token.evaluate(ctx) for token in self.tokens)
        # Split lists.
        list = [item for token in list for item in token.split(';')]
        return list
