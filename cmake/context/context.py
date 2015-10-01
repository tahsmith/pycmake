__author__ = 'tahsmith'


class Context(object):
    variable_stack = [dict()]
    cache_variables = dict()
    targets = dict()
    callables = dict()

    def variable_lookup(self, name):
        """
        :param name:
        :return:
        """
        for scope in reversed(self.variable_stack):
            if name in scope:
                return scope[name]
        return None
