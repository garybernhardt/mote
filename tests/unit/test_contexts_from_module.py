from dingus import Dingus, DingusFixture
import mote
from mote import ContextsFromModule


class WhenModuleContainsContextFunctions(DingusFixture(ContextsFromModule)):
    def setup(self):
        super(WhenModuleContainsContextFunctions, self).setup()
        self.describe_foo = lambda: None
        self.describe_foo.__name__ = 'describe_foo'
        self.contexts = ContextsFromModule([self.describe_foo])

    def should_create_context_(self):
        assert mote.Context.calls('()', self.describe_foo)

    def should_include_context_function(self):
        assert self.contexts == [mote.Context.return_value]


class WhenModuleContainsOtherCallables(DingusFixture(ContextsFromModule)):
    def setup(self):
        super(WhenModuleContainsOtherCallables, self).setup()
        self.some_function = lambda: None
        self.contexts = ContextsFromModule([self.some_function])

    def should_not_include_other_functions(self):
        assert self.contexts == []


class WhenModuleContainsVariables(DingusFixture(ContextsFromModule)):
    def setup(self):
        super(WhenModuleContainsVariables, self).setup()
        self.contexts = ContextsFromModule([1])

    def should_not_include_variable(self):
        assert len(self.contexts) == 0

    def should_not_try_to_collect_tests_from_noncallables(self):
        assert not mote.Context.calls('()')

