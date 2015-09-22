__author__ = 'tahsmith'

from unittest import TestCase

from parser import *

class TestParser(TestCase):
    def test_variable(self):
        variable_reference.parseString("")