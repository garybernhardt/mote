import sys

from dingus import Dingus, DingusFixture
import mote
from mote import LocalFunctions


class BaseFixture(DingusFixture(LocalFunctions)):
    def setup(self):
        super(BaseFixture, self).setup()
        mote.sys = sys


class WhenExaminingFunctionWithALocalFunction(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithALocalFunction, self).setup()
        def function():
            def local_function():
                return 'local function return'

        self.local_functions = LocalFunctions(function, '')

    def should_have_correct_number_of_local_function(self):
        assert len(self.local_functions) == 1

    def should_find_local_function_object(self):
        local_function = self.local_functions[0]
        assert local_function() == 'local function return'

    def should_return_functions_by_name(self):
        local_function = self.local_functions.function_with_name(
            'local_function')
        assert local_function() == 'local function return'


class WhenExaminingFunctionWithLocalVariables(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithLocalVariables, self).setup()
        def function():
            local_variable = 1
        self.local_functions = LocalFunctions(function, '')

    def should_not_include_local_variable(self):
        assert not self.local_functions


class WhenExtractingCases(BaseFixture):
    def setup(self):
        super(WhenExtractingCases, self).setup()
        def context_function():
            def should_do_something(): pass
            def some_function(): pass

        self.local_functions = LocalFunctions.case_functions(context_function)

    def should_only_include_functions_starting_with_the_prefix(self):
        assert (len(self.local_functions) == 1 and
                self.local_functions[0].__name__ == 'should_do_something')

