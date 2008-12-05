import sys

from dingus import Dingus, DingusFixture
import mote
from mote import LocalFunctions


BaseFixture = DingusFixture(LocalFunctions)


class WhenExaminingFunctionWithALocalFunction(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithALocalFunction, self).setup()
        mote.sys = sys
        def function():
            def local_function():
                return 'local function return'

        self.local_functions = LocalFunctions(function)

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
        mote.sys = sys
        def function():
            local_variable = 1
        self.local_functions = LocalFunctions(function)

    def should_not_include_local_variable(self):
        assert not self.local_functions

