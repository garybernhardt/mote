import sys
import re
from types import FunctionType

from dingus import Dingus, DingusTestCase
from mote import localfunctions
from mote.localfunctions import LocalFunctions


class BaseFixture(DingusTestCase(LocalFunctions)):
    def setup(self):
        super(BaseFixture, self).setup()
        localfunctions.re = re
        localfunctions.FunctionType = FunctionType


class WhenExaminingFunctionWithALocalFunction(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithALocalFunction, self).setup()
        def local_function():
            return 'local function return'
        localfunctions.FunctionLocals.return_value = [local_function]
        self.local_functions = LocalFunctions(Dingus())

    def should_return_functions_by_name(self):
        local_function = self.local_functions.function_with_name(
            'local_function')
        assert local_function() == 'local function return'


class WhenExaminingFunctionWithLocalVariables(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithLocalVariables, self).setup()
        localfunctions.FunctionLocals.return_value = ['not a function']
        self.local_function = LocalFunctions(Dingus(), '')

    def should_not_include_local_variable(self):
        assert self.local_function == []


class WhenExaminingFunctionWithLocalCallable(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithLocalCallable, self).setup()
        class Callable:
            def __call__(self):
                pass
        localfunctions.FunctionLocals.return_value = [Callable()]
        self.local_function = LocalFunctions(Dingus(), '')

    def should_not_include_callable_that_isnt_function(self):
        assert self.local_function == []


class WhenExtractingCases(BaseFixture):
    def setup(self):
        super(WhenExtractingCases, self).setup()
        def does_something(): pass
        def _some_non_spec_function(): pass
        def when_doing_something(): pass
        self.does_something = does_something
        self.when_doing_something = when_doing_something
        localfunctions.FunctionLocals.return_value = [does_something,
                                                      _some_non_spec_function,
                                                      when_doing_something]

        self.local_functions = LocalFunctions.case_functions(Dingus())

    def should_include_functions(self):
        assert self.does_something in self.local_functions

    def should_not_include_contexts(self):
        assert self.when_doing_something not in self.local_functions


class WhenExtractingContexts(BaseFixture):
    def setup(self):
        super(WhenExtractingContexts, self).setup()
        def when_doing_something(): pass
        def some_function(): pass
        localfunctions.FunctionLocals.return_value = [when_doing_something,
                                            some_function]

        self.local_functions = LocalFunctions.context_functions(Dingus())

    def should_only_include_context_functions(self):
        assert (len(self.local_functions) == 1 and
                self.local_functions[0].__name__ == 'when_doing_something')

