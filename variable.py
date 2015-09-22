__author__ = 'tahsmith'

from operator import add


class Identifier(object):
    def __init__(self, token):
        self.fragment = token

    def interpolate(self, table):
        return self.fragment


class InterpolatedIdentifier(object):
    def __init__(self, token):
        self.fragments = token

    def interpolate(self, table):
        return reduce(add, (fragment.interpolate() for fragment in self.fragments))


class VariableReference(object):
    def __init__(self, token):
        self.name = token

    def interpolate(self, table):
        return table[self.name]