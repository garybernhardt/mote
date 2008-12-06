from dingus import Dingus, DingusFixture, DontCare
import mote
from mote import SpecSuite


BaseFixture = DingusFixture(SpecSuite)

class WhenModuleContainsCallables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsCallables, self).setup()
        mote.Context.return_value.run.return_value = []
        self.context_function = lambda: None
        self.suite = SpecSuite(dict(context_function=self.context_function))
        self.suite.run()

    def should_create_context_(self):
        assert mote.Context.calls('()', self.context_function)

    def should_run_context(self):
        assert mote.Context.return_value.calls('run').one()


class WhenModuleContainsVariables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsVariables, self).setup()
        self.suite = SpecSuite(dict(variable=1))
        self.suite.run()

    def should_not_try_to_collect_tests_from_noncallables(self):
        assert not mote.LocalFunctions.calls('()')


class WhenRunningPassingTests(BaseFixture):
    def setup(self):
        super(WhenRunningPassingTests, self).setup()
        case_result = Dingus(success=True)
        mote.Context.return_value.run.return_value = [case_result]
        self.suite = SpecSuite({})
        self.suite.run()

    def should_indicate_success(self):
        assert self.suite.success


class WhenRunningFailingTests(BaseFixture):
    def setup(self):
        super(WhenRunningFailingTests, self).setup()
        case_result = Dingus(success=False)
        mote.Context.return_value.run.return_value = [case_result]

        self.context_function = lambda: None
        self.suite = SpecSuite(dict(context_function=self.context_function))
        self.suite.run()

    def should_indicate_failure(self):
        assert not self.suite.success

