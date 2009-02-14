import sys

from dingus import Dingus, DingusTestCase
import mote
from mote import LocalFunctions


BaseFixture = DingusTestCase(LocalFunctions)


class WhenExaminingFunctionWithALocalFunction(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithALocalFunction, self).setup()
        def local_function():
            return 'local function return'
        mote.FunctionLocals.return_value = [local_function]
        self.local_functions = LocalFunctions(Dingus(), '')

    def should_return_functions_by_name(self):
        local_function = self.local_functions.function_with_name(
            'local_function')
        assert local_function() == 'local function return'


class WhenExaminingFunctionWithLocalVariables(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithLocalVariables, self).setup()
        mote.FunctionLocals.return_value = ['not a function']
        self.local_function = LocalFunctions(Dingus(), '')

    def should_not_include_local_variable(self):
        assert self.local_function == []


class WhenExtractingCases(BaseFixture):
    def setup(self):
        super(WhenExtractingCases, self).setup()
        def should_do_something(): pass
        def some_function(): pass
        mote.FunctionLocals.return_value = [should_do_something,
                                            some_function]

        self.local_functions = LocalFunctions.case_functions(Dingus())

    def should_only_include_functions_starting_with_the_prefix(self):
        assert (len(self.local_functions) == 1 and
                self.local_functions[0].__name__ == 'should_do_something')


class WhenExtractingContexts(BaseFixture):
    def setup(self):
        super(WhenExtractingContexts, self).setup()
        def when_doing_something(): pass
        def some_function(): pass
        mote.FunctionLocals.return_value = [when_doing_something,
                                            some_function]

        self.local_functions = LocalFunctions.context_functions(Dingus())

    def should_only_include_context_functions(self):
        assert (len(self.local_functions) == 1 and
                self.local_functions[0].__name__ == 'when_doing_something')

