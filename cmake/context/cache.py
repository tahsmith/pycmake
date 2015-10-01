__author__ = 'tahsmith'

class CacheVariable(object):
    def __init__(self, value, type='STRING', desc=''):
        self.value = value
        self.type = type
        self.desc = desc

    def __eq__(self, other):
        return self.value == other

    def __hash__(self):
        return hash(self.value)