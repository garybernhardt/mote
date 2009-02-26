from dingus import Dingus, DingusTestCase, DontCare
import mote
from mote import SpecSuite


class BaseFixture(DingusTestCase(SpecSuite)):
    def setup(self):
        super(BaseFixture, self).setup()
        self.describe_foo = lambda: None
        self.describe_foo.__name__ = 'describe_foo'
        self.describe_bar = lambda: None
        self.describe_bar.__name__ = 'describe_bar'


class WhenModuleContainsContextFunctions(BaseFixture):
    def setup(self):
        super(WhenModuleContainsContextFunctions, self).setup()
        self.suite = SpecSuite([dict(describe_foo=self.describe_foo)])

    def should_create_context_(self):
        assert mote.Context.calls('()', self.describe_foo)

    def should_include_context_in_list(self):
        assert self.suite.contexts == [mote.Context.return_value]


class WhenModuleContainsOtherCallables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsOtherCallables, self).setup()
        self.some_function = lambda: None
        some_fn = lambda: None
        some_fn.__name__ = 'some_fn'
        self.suite = SpecSuite([dict(some_fn=some_fn)])

    def should_not_include_other_functions(self):
        assert self.suite.contexts == []


class WhenModuleContainsVariables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsVariables, self).setup()
        self.suite = SpecSuite([dict(variable=1)])

    def should_not_include_variable(self):
        assert len(self.suite.contexts) == 0

    def should_not_try_to_collect_tests_from_noncallables(self):
        assert not mote.Context.calls

class WhenRunningPassingContexts(BaseFixture):
    def setup(self):
        super(WhenRunningPassingContexts, self).setup()
        mote.Context.return_value = Dingus(success=True)
        self.suite = SpecSuite([dict(describe_foo=self.describe_foo)])

    def should_indicate_success(self):
        assert self.suite.success

    def should_find_contexts_function(self):
        assert mote.Context.calls('()').one()


class WhenRunningFailingContexts(BaseFixture):
    def setup(self):
        super(WhenRunningFailingContexts, self).setup()
        mote.Context.return_value = Dingus(success=False)
        self.suite = SpecSuite([dict(describe_foo=self.describe_foo)])

    def should_indicate_failure(self):
        assert not self.suite.success

    def should_find_contexts_function(self):
        assert mote.Context.calls('()').one()


class WhenGivenMultipleModules(BaseFixture):
    def setup(self):
        super(WhenGivenMultipleModules, self).setup()
        self.modules = [dict(describe_foo=self.describe_foo),
                        dict(describe_bar=self.describe_bar)]
        self.ctx_functions = [self.describe_foo, self.describe_bar]
        self.suite = SpecSuite(self.modules)

    def should_build_contexts_from_context_functions_in_all_modules(self):
        assert all(mote.Context.calls('()', ctx_function).one()
                   for ctx_function in self.ctx_functions)

    def should_collect_all_contexts(self):
        assert self.suite.contexts == [mote.Context.return_value] * 2

