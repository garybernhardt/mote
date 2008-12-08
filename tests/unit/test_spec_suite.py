from dingus import Dingus, DingusFixture, DontCare
import mote
from mote import SpecSuite


BaseFixture = DingusFixture(SpecSuite)


class WhenModuleContainsCallables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsCallables, self).setup()
        mote.CasesFromContexts.return_value = []
        self.context_function = lambda: None
        self.suite = SpecSuite(dict(context_function=self.context_function))
        self.suite.run()

    def should_create_context_(self):
        assert mote.Context.calls('()', self.context_function)

    def should_collect_cases_from_contexts(self):
        assert mote.CasesFromContexts.calls('()', [mote.Context.return_value])


class WhenModuleContainsVariables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsVariables, self).setup()
        mote.CasesFromContexts.return_value = []
        self.suite = SpecSuite(dict(variable=1))
        self.suite.run()

    def should_not_try_to_collect_tests_from_noncallables(self):
        assert not mote.LocalFunctions.calls('()')


class WhenRunningPassingTests(BaseFixture):
    def setup(self):
        super(WhenRunningPassingTests, self).setup()
        case = Dingus(success=True)
        mote.CasesFromContexts.return_value = [case]
        self.suite = SpecSuite({})
        self.suite.run()

    def should_indicate_success(self):
        assert self.suite.success


class WhenRunningFailingTests(BaseFixture):
    def setup(self):
        super(WhenRunningFailingTests, self).setup()
        case = Dingus(success=False)
        mote.CasesFromContexts.return_value = [case]

        self.context_function = lambda: None
        self.suite = SpecSuite(dict(context_function=self.context_function))
        self.suite.run()

    def should_indicate_failure(self):
        assert not self.suite.success


class WhenRunning(BaseFixture):
    def setup(self):
        super(WhenRunning, self).setup()
        self.cases = [Dingus(success=True) for _ in range(2)]
        mote.CasesFromContexts.return_value = self.cases

        self.context_function = lambda: None
        self.suite = SpecSuite(dict(context_function=self.context_function))
        self.suite_result = self.suite.run()

    def should_return_correct_number_of_cases(self):
        assert self.suite_result == self.cases

