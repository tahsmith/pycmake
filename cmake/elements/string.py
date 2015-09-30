__author__ = 'tahsmith'

from argument import VariableReference, VariableStack
from operator import add

class StringFragment(object):
    def __init__(self, tokens):
        self.fragment = tokens[0]

    def interpolate(self, stack):
        return self.fragment

class String(object):
    def __init__(self, tokens):
        self.fragments = tokens

    def interpolate(self, stack):
        return reduce(add, (fragment.interpolate(stack) for fragment in self.fragments))

