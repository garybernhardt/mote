import sys
import re
from types import FunctionType

from dingus import Dingus, DingusTestCase
from mote import localfunctions as mod
from mote.localfunctions import LocalFunctions


class BaseFixture(DingusTestCase(mod.LocalFunctions,
                                 exclude=['FunctionLocals',
                                          'sys',
                                          'FunctionType'])):
    def setup(self):
        super(BaseFixture, self).setup()


class WhenExaminingFunctionWithALocalFunction(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithALocalFunction, self).setup()
        def parent_function():
            def local_function():
                return 'local function return'
            def other_local_function():
                return 'other local function return'
        self.local_functions = LocalFunctions(parent_function)

    def should_return_functions_by_name(self):
        local_function = self.local_functions.function_with_name(
            'local_function')
        assert local_function() == 'local function return'

    def should_find_multiple_functions(self):
        assert len(self.local_functions) == 2

    def should_sort_functions_by_line_number(self):
        def parent_function():
            def local_function(): return 'first'
            def other_local_function(): return 'second'
        def parent_function_reversed():
            def other_local_function(): return 'first'
            def local_function(): return 'second'
        assert (LocalFunctions(parent_function)[0]() ==
                LocalFunctions(parent_function_reversed)[0]() ==
                'first')


class WhenExaminingFunctionWithLocalVariables(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithLocalVariables, self).setup()
        self.local_function = LocalFunctions(Dingus(), '')

    def should_not_include_local_variable(self):
        assert self.local_function == []


class WhenExaminingFunctionWithLocalCallable(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithLocalCallable, self).setup()
        class Callable:
            def __call__(self):
                pass
        self.local_function = LocalFunctions(Dingus(), '')

    def should_not_include_callable_that_isnt_function(self):
        assert self.local_function == []


class WhenExtractingCases(BaseFixture):
    def setup(self):
        super(WhenExtractingCases, self).setup()
        def parent_function():
            def does_something(): return 'does_something'
            def _some_non_spec_function(): return '_some_non_spec_function'
            def describe_doing_something(): return 'describe_doing_something'
        self.local_functions = LocalFunctions.case_functions(parent_function)
        self.all_return_values = [fn() for fn in self.local_functions]

    def should_include_case_functions(self):
        assert 'does_something' in self.all_return_values

    def should_not_include_contexts(self):
        assert 'describe_doing_something' not in self.all_return_values


class WhenExtractingContexts(BaseFixture):
    def setup(self):
        super(WhenExtractingContexts, self).setup()
        def parent_function():
            def describe_doing_something(): return 'describe_doing_something'
            def some_function(): return 'some_function'
        self.functions = LocalFunctions.context_functions(parent_function)

    def should_only_include_context_functions(self):
        assert (len(self.functions) == 1 and
                self.functions[0]() == 'describe_doing_something')

