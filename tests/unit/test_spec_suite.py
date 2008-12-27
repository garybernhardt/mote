from dingus import Dingus, DingusTestCase, DontCare
import mote
from mote import SpecSuite


BaseFixture = DingusTestCase(SpecSuite)


class WhenModuleContainsCallables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsCallables, self).setup()
        mote.ContextsFromModule.return_value = []
        self.module_contents = Dingus()
        self.suite = SpecSuite([self.module_contents])

    def should_collect_contexts_from_module(self):
        assert mote.ContextsFromModule.calls(
            '()', self.module_contents.values.return_value)


class WhenRunningPassingTests(BaseFixture):
    def setup(self):
        super(WhenRunningPassingTests, self).setup()
        context = Dingus(success=True)
        mote.ContextsFromModule.return_value = [context]
        self.suite = SpecSuite([{}])

    def should_indicate_success(self):
        assert self.suite.success


class WhenRunningFailingTests(BaseFixture):
    def setup(self):
        super(WhenRunningFailingTests, self).setup()
        context = Dingus(success=False)
        mote.ContextsFromModule.return_value = [context]

        self.suite = SpecSuite([{}])

    def should_indicate_failure(self):
        assert not self.suite.success


class WhenRunning(BaseFixture):
    def setup(self):
        super(WhenRunning, self).setup()
        self.cases = [Dingus(success=True) for _ in range(2)]
        self.context = Dingus()
        mote.ContextsFromModule.return_value = [self.context]

        self.context_function = lambda: None
        self.suite = SpecSuite([dict(context_function=self.context_function)])

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

