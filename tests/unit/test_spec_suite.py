from dingus import Dingus, DingusFixture, DontCare
import mote
from mote import SpecSuite


class BaseFixture(DingusFixture(SpecSuite)):
    def _add_context_function(self):
        def function_in_module():
            pass
        self.context_function = function_in_module
        mote.ImportedModule.return_value = {'context_function':
                                            self.context_function}


class WhenCreatingSuite(BaseFixture):
    def setup(self):
        super(WhenCreatingSuite, self).setup()
        mote.ImportedModule.return_value = {}
        self.filename = 'spec_foo.py'
        self.suite = SpecSuite(self.filename)

    def should_not_import_spec_file(self):
        assert not mote.ImportedModule.calls


class WhenModuleContainsCallables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsCallables, self).setup()
        self._add_context_function()
        self.suite = SpecSuite(Dingus())
        self.suite.run()

    def should_create_context_(self):
        assert mote.Context.calls('()', self.context_function)

    def should_run_context(self):
        assert mote.Context.return_value.calls('run').one()


class WhenModuleContainsVariables(BaseFixture):
    def setup(self):
        super(WhenModuleContainsVariables, self).setup()
        self.variable = 1
        mote.ImportedModule.return_value = {'variable': self.variable}
        self.suite = SpecSuite(Dingus())
        self.suite.run()

    def should_not_try_to_collect_tests_from_noncallables(self):
        assert not mote.LocalFunctions.calls('()', self.variable)


class WhenRunningPassingTests(BaseFixture):
    def setup(self):
        super(WhenRunningPassingTests, self).setup()
        mote.ImportedModule.return_value = {}
        self.filename = 'spec_foo.py'
        self.suite = SpecSuite(self.filename)
        self.suite.run()

    def should_import_spec_file(self):
        assert mote.ImportedModule.calls('()', self.filename)

    def should_indicate_success(self):
        assert self.suite.success


class WhenRunningFailingTests(BaseFixture):
    def setup(self):
        super(WhenRunningFailingTests, self).setup()
        self._add_context_function()
        mote.Context.return_value.success = False
        self.suite = SpecSuite(Dingus())
        self.suite.run()

    def should_indicate_failure(self):
        assert not self.suite.success
