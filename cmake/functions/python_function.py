from cmake.context import Context

__author__ = 'tahsmith'


class PythonFunction(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, context, argument_list):
        self.func(*argument_list)