import sys
import re
from types import FunctionType

from dingus import Dingus, DingusTestCase
from mote import localfunctions as mod
from mote.localfunctions import LocalFunctions


class BaseFixture(DingusTestCase(mod.LocalFunctions,
                                 'FunctionLocals',
                                 'sys',
                                 'FunctionType')):
    def setup(self):
        super(BaseFixture, self).setup()


class WhenExaminingFunctionWithALocalFunction(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithALocalFunction, self).setup()
        def parent_function():
            def local_function():
                return 'local function return'
        self.local_functions = LocalFunctions(parent_function)

    def should_return_functions_by_name(self):
        local_function = self.local_functions.function_with_name(
            'local_function')
        assert local_function() == 'local function return'


class WhenExaminingFunctionWithLocalVariables(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithLocalVariables, self).setup()
        mod.FunctionLocals.return_value = ['not a function']
        self.local_function = LocalFunctions(Dingus(), '')

    def should_not_include_local_variable(self):
        assert self.local_function == []


class WhenExaminingFunctionWithLocalCallable(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithLocalCallable, self).setup()
        class Callable:
            def __call__(self):
                pass
        mod.FunctionLocals.return_value = [Callable()]
        self.local_function = LocalFunctions(Dingus(), '')

    def should_not_include_callable_that_isnt_function(self):
        assert self.local_function == []


class WhenExtractingCases(BaseFixture):
    def setup(self):
        super(WhenExtractingCases, self).setup()
        def parent_function():
            def does_something(): return 'does_something'
            def _some_non_spec_function(): return '_some_non_spec_function'
            def when_doing_something(): return 'when_doing_something'
        self.local_functions = LocalFunctions.case_functions(parent_function)
        self.all_return_values = [fn() for fn in self.local_functions]

    def should_include_case_functions(self):
        assert 'does_something' in self.all_return_values

    def should_not_include_contexts(self):
        assert 'when_doing_something' not in self.all_return_values


class WhenExtractingContexts(BaseFixture):
    def setup(self):
        super(WhenExtractingContexts, self).setup()
        def parent_function():
            def when_doing_something(): return 'when_doing_something'
            def some_function(): return 'some_function'
        self.functions = LocalFunctions.context_functions(parent_function)

    def should_only_include_context_functions(self):
        assert (len(self.functions) == 1 and
                self.functions[0]() == 'when_doing_something')

