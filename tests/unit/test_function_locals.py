import sys

from dingus import Dingus, DingusFixture
import mote
from mote import FunctionLocals


BaseFixture = DingusFixture(FunctionLocals)


class WhenExaminingFunctionWithALocalFunction(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithALocalFunction, self).setup()
        mote.sys = sys
        def function():
            def local_function():
                return 'local function return'

        self.function_locals = FunctionLocals(function)

    def should_have_correct_number_of_local_function(self):
        assert len(self.function_locals) == 1

    def should_find_local_function_object(self):
        local_function = self.function_locals[0]
        assert local_function() == 'local function return'
