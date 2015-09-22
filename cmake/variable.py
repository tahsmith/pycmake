__author__ = 'tahsmith'

from operator import add


class VariableStack(object):
    stack = list()

    def __init__(self, *args, **kwargs):
        super(VariableStack, self).__init__(*args, **kwargs)

    def search(self, id):
        self.search()


class IdentifierFragment(object):
    def __init__(self, token):
        self.fragment = token[0]

    def interpolate(self, variable_stack):
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