from dingus import Dingus, DingusFixture
import mote
from mote import Context


class BaseFixture(DingusFixture(Context)):
    def setup(self):
        super(BaseFixture, self).setup()

    def _run_context_with_case_function(self, case_function):
        self.context_function = Dingus()
        mote.LocalFunctions.return_value = [self.case_function]
        self.context = Context(self.context_function)
        self.context.run()


class WhenRunningContextFromFunction(BaseFixture):
    def setup(self):
        super(WhenRunningContextFromFunction, self).setup()
        self.case_function = Dingus()
        self._run_context_with_case_function(self.case_function)

    def should_extract_spec_cases(self):
        assert mote.LocalFunctions.calls('()', self.context_function)

    def should_run_functions_in_context(self):
        assert self.case_function.calls


class WhenTestFunctionsRaiseNoExceptions(BaseFixture):
    def setup(self):
        super(WhenTestFunctionsRaiseNoExceptions, self).setup()
        self.case_function = Dingus()
        self._run_context_with_case_function(self.case_function)

    def should_indicate_success(self):
        assert self.context.success


class WhenRunningFunctionsInDifferentOrders(BaseFixture):
    def setup(self):
        super(WhenRunningFunctionsInDifferentOrders, self).setup()
        self.function_calls = []
        self.case_function_parent = Dingus()
        self.case_function_parent.func1.func_code.co_firstlineno = 1
        self.case_function_parent.func2.func_code.co_firstlineno = 2
        self.case_functions = [self.case_function_parent.func1,
                               self.case_function_parent.func2]

    def _create_context_with_case_functions(self, case_functions):
        mote.LocalFunctions.return_value = case_functions
        context = Context(Dingus())
        context.run()

    def _case_calls(self):
        return [call.name for call in self.case_function_parent.calls]

    def should_sort_functions(self):
        self._create_context_with_case_functions(self.case_functions)
        assert self._case_calls() == ['func1', 'func2']

    def should_sort_functions_when_reversed(self):
        case_functions = list(reversed(self.case_functions))
        self._create_context_with_case_functions(case_functions)
        assert self._case_calls() == ['func1', 'func2']

