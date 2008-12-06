from dingus import Dingus, DingusFixture, exception_raiser
import mote
from mote import Case


class WhenRunningCase(DingusFixture(Case)):
    def setup(self):
        super(WhenRunningCase, self).setup()
        self.context_function, self.case_name = Dingus.many(2)
        case = Case(self.context_function, self.case_name)
        case.run()

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
        case = Case(self.context_function, self.case_name)
        self.case_result = case.run()

    def should_return_successful_case_results(self):
        assert self.case_result is mote.CaseResult.success.return_value

    def should_include_name_in_case_result(self):
        assert mote.CaseResult.calls('success', self.case_name).one()


class WhenTestFunctionRaisesException(DingusFixture(Case)):
    def setup(self):
        super(WhenTestFunctionRaisesException, self).setup()
        local_functions = mote.LocalFunctions.return_value
        local_functions.function_with_name.return_value = exception_raiser(
            AssertionError)

        self.context_function, self.case_name = Dingus.many(2)
        case = Case(self.context_function, self.case_name)
        self.case_result = case.run()

    def should_return_failed_case_results(self):
        assert self.case_result is mote.CaseResult.failure.return_value

    def should_include_name_in_case_result(self):
        assert mote.CaseResult.calls('failure', self.case_name).one()

