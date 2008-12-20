from dingus import Dingus, DingusTestCase, DontCare
import mote
from mote import ImportedModule

class WhenImportingModule(DingusTestCase(ImportedModule)):
    def setup(self):
        super(WhenImportingModule, self).setup()
        self.some_default_global = Dingus()
        mote.DEFAULT_GLOBALS = {'some_default_global':
                                self.some_default_global}
        mote.execfile = Dingus()
        self.filename = 'spec_foo.py'
        self.module = ImportedModule(self.filename)

    def should_import_file(self):
        assert mote.execfile.calls('()', self.filename, DontCare)

    def should_import_globals(self):
        assert mote.execfile.calls('()', DontCare, self.module)

    def should_be_dict(self):
        assert isinstance(self.module, dict)

    def should_include_default_globals(self):
        globals_ = mote.execfile.calls('()', DontCare, DontCare).one().args[1]
        assert globals_['some_default_global'] is self.some_default_global

