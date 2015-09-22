__author__ = 'tahsmith'

from operator import add


class IdentifierFragment(object):
    def __init__(self, token):
        self.fragment = token[0]

    def interpolate(self, table):
        return self.fragment


class InterpolatedIdentifier(object):
    def __init__(self, token):
        self.fragments = token

    def interpolate(self, table):
        return reduce(add, (fragment.interpolate(table) for fragment in self.fragments))


class VariableReference(object):
    def __init__(self, token):
        self.identifier = token[0]
        assert type(self.identifier) == InterpolatedIdentifier

    def interpolate(self, table):
        return table[self.identifier.interpolate(table)]