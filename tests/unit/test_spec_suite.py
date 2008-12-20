from dingus import Dingus, DingusTestCase, DontCare
import mote
from mote import SpecSuite


BaseFixture = DingusTestCase(SpecSuite)


class WhenModuleContainsCallables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsCallables, self).setup()
        mote.ContextsFromModule.return_value = []
        mote.CasesFromContexts.return_value = []
        self.module_contents = Dingus()
        self.suite = SpecSuite([self.module_contents])
        self.suite.run()

    def should_collect_contexts_from_module(self):
        assert mote.ContextsFromModule.calls(
            '()', self.module_contents.values.return_value)

    def should_collect_cases_from_contexts(self):
        assert mote.CasesFromContexts.calls(
            '()', mote.ContextsFromModule.return_value)


class WhenRunningPassingTests(BaseFixture):
    def setup(self):
        super(WhenRunningPassingTests, self).setup()
        case = Dingus(success=True)
        mote.CasesFromContexts.return_value = [case]
        mote.ContextsFromModule.return_value = []
        self.suite = SpecSuite([{}])
        self.suite.run()

    def should_indicate_success(self):
        assert self.suite.success


class WhenRunningFailingTests(BaseFixture):
    def setup(self):
        super(WhenRunningFailingTests, self).setup()
        case = Dingus(success=False)
        mote.CasesFromContexts.return_value = [case]
        mote.ContextsFromModule.return_value = []

        self.context_function = lambda: None
        self.suite = SpecSuite([dict(context_function=self.context_function)])
        self.suite.run()

    def should_indicate_failure(self):
        assert not self.suite.success


class WhenRunning(BaseFixture):
    def setup(self):
        super(WhenRunning, self).setup()
        self.cases = [Dingus(success=True) for _ in range(2)]
        mote.CasesFromContexts.return_value = self.cases
        self.context = Dingus()
        mote.ContextsFromModule.return_value = [self.context]

        self.context_function = lambda: None
        self.suite = SpecSuite([dict(context_function=self.context_function)])
        self.suite_result = self.suite.run()

    def should_expose_contexts(self):
        assert self.suite.contexts == [self.context]


class WhenGivenMultipleModules(BaseFixture):
    def setup(self):
        super(WhenGivenMultipleModules, self).setup()
        self.modules = Dingus.many(2)
        self.contexts = [Dingus()]
        mote.ContextsFromModule.return_value = self.contexts
        self.suite = SpecSuite(self.modules)

    def should_extract_contexts_from_all_modules(self):
        assert all(
            mote.ContextsFromModule.calls('()',
                                          module.values.return_value).one()
            for module in self.modules)

    def should_collect_all_contexts(self):
        assert self.suite.contexts == self.contexts * 2

