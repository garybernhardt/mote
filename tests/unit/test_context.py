from dingus import Dingus, DingusFixture
import mote
from mote import Context


class BaseFixture(DingusFixture(Context)):
    def setup(self):
        super(BaseFixture, self).setup()

    def _run_context_with_case_function(self, case_function):
        self.context_function = Dingus()
        mote.LocalFunctions.return_value = [self.case_function]
        mote.SortedFunctions.return_value = [self.case_function]
        self.context = Context(self.context_function)
        self.context.run()


class WhenRunningContextFromFunction(BaseFixture):
    def setup(self):
        super(WhenRunningContextFromFunction, self).setup()
        self.case_function = Dingus()
        self._run_context_with_case_function(self.case_function)

    def should_extract_spec_cases(self):
        assert mote.LocalFunctions.calls('()', self.context_function)

    def should_sort_functions(self):
        assert mote.SortedFunctions.calls('()', [self.case_function])


class WhenRunningMultipleCases(BaseFixture):
    def setup(self):
        super(WhenRunningMultipleCases, self).setup()
        self.context_function = Dingus()
        self.case_functions = [Dingus(), Dingus()]
        mote.SortedFunctions.return_value = self.case_functions
        context = Context(self.context_function)
        context.run()

    def should_create_cases(self):
        assert all(mote.Case.calls('()',
                                   self.context_function,
                                   case_function.__name__).one()
                   for case_function in self.case_functions)

    def should_run_cases(self):
        case = mote.Case.return_value
        assert len(case.calls('run')) == len(self.case_functions)


class WhenTestFunctionsRaiseNoExceptions(BaseFixture):
    def setup(self):
        super(WhenTestFunctionsRaiseNoExceptions, self).setup()
        self.case_function = Dingus()
        self._run_context_with_case_function(self.case_function)

    def should_indicate_success(self):
        assert self.context.success

