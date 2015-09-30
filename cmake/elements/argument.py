__author__ = 'tahsmith'

from operator import add


class VariableStack(object):
    stack = list()

    def __init__(self, *args, **kwargs):
        super(VariableStack, self).__init__(*args, **kwargs)

    def search(self, id):
        self.search()


class Fragment(object):
    def __init__(self):
        pass


class VariableReference(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def interpolate(self, env):
        return reduce(add, (token.interpolate(env) for token in self.tokens))


class EnvironmentVariableReference(object):
    pass


class InterpolatedString(object):
    def __init__(self, tokens):
        self.elements = tokens