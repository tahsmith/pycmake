from cmake.context import Context

__author__ = 'tahsmith'


class PythonFunction(object):
    def __init__(self, func):
        self.func = func

    def invoke(self, ctx, argument_list):
        self.func(*argument_list)