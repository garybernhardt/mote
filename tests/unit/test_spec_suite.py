from dingus import Dingus, DingusFixture, DontCare
import mote
from mote import SpecSuite


class WhenCreatingSuite(DingusFixture(SpecSuite)):
    def setup(self):
        super(WhenCreatingSuite, self).setup()
        mote.ImportedModule.return_value = {}
        mote.execfile = Dingus()
        self.filename = 'spec_foo.py'
        self.suite = SpecSuite(self.filename)

    def should_not_import_spec_file(self):
        assert not mote.ImportedModule.calls


class WhenRunningTests(DingusFixture(SpecSuite)):
    def setup(self):
        super(WhenRunningTests, self).setup()
        mote.ImportedModule.return_value = {}
        self.filename = 'spec_foo.py'
        self.suite = SpecSuite(self.filename)
        self.suite.run()

    def should_import_spec_file(self):
        assert mote.ImportedModule.calls('()', self.filename)


class WhenModuleContainsCallables(DingusFixture(SpecSuite)):
    def setup(self):
        super(WhenModuleContainsCallables, self).setup()
        def function_in_module():
            pass
        self.context_function = function_in_module
        mote.ImportedModule.return_value = {'context_function':
                                            self.context_function}
        self.suite = SpecSuite(Dingus())
        self.suite.run()

    def should_create_context_(self):
        assert mote.Context.calls('()', self.context_function)

    def should_run_context(self):
        assert mote.Context.return_value.calls('run').one()


class WhenModuleContainsVariables(DingusFixture(SpecSuite)):
    def setup(self):
        super(WhenModuleContainsVariables, self).setup()
        self.variable = 1
        mote.ImportedModule.return_value = {'variable': self.variable}
        self.suite = SpecSuite(Dingus())
        self.suite.run()

    def should_not_try_to_collect_tests_from_noncallables(self):
        assert not mote.LocalFunctions.calls('()', self.variable)

