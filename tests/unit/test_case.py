from dingus import Dingus, DingusFixture, exception_raiser
import mote
from mote import Case


class WhenRunningCase(DingusFixture(Case)):
    def setup(self):
        super(WhenRunningCase, self).setup()
        self.context_function, self.case_name = Dingus.many(2)
        case = Case(self.context_function, self.case_name)

    def should_get_local_functions_from_context_to_ensure_isolation(self):
        assert mote.LocalFunctions.calls('()', self.context_function).one()

    def should_run_cases_with_fresh_context(self):
        local_functions = mote.LocalFunctions.return_value
        case_function = local_functions.calls(
            'function_with_name', self.case_name).one().return_value
        assert case_function.calls('()').one()


class WhenTestFunctionRaisesNoException(DingusFixture(Case)):
    def setup(self):
        super(WhenTestFunctionRaisesNoException, self).setup()
        self.context_function, self.case_name = Dingus.many(2)
        self.case = Case(self.context_function, self.case_name)

    def should_run_successfully(self):
        assert self.case.success


class WhenTestFunctionRaisesException(DingusFixture(Case)):
    def setup(self):
        super(WhenTestFunctionRaisesException, self).setup()
        local_functions = mote.LocalFunctions.return_value
        local_functions.function_with_name.return_value = exception_raiser(
            AssertionError)

        self.context_function, self.case_name = Dingus.many(2)
        self.case = Case(self.context_function, self.case_name)

    def should_fail(self):
        assert not self.case.success

