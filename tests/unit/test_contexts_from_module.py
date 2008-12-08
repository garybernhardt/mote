from dingus import Dingus, DingusFixture
import mote
from mote import ContextsFromModule


class WhenModuleContainsCallables(DingusFixture(ContextsFromModule)):
    def setup(self):
        super(WhenModuleContainsCallables, self).setup()
        self.context_function = lambda: None
        self.contexts = ContextsFromModule([self.context_function])

    def should_create_context_(self):
        assert mote.Context.calls('()', self.context_function)

    def should_include_context_function(self):
        assert self.contexts == [mote.Context.return_value]


class WhenModuleContainsVariables(DingusFixture(ContextsFromModule)):
    def setup(self):
        super(WhenModuleContainsVariables, self).setup()
        self.contexts = ContextsFromModule([1])

    def should_not_include_variable(self):
        assert len(self.contexts) == 0

    def should_not_try_to_collect_tests_from_noncallables(self):
        assert not mote.Context.calls('()')
