from dingus import Dingus, DingusFixture, DontCare
import mote
from mote import ImportedModule

class WhenImportingModule(DingusFixture(ImportedModule)):
    def setup(self):
        super(WhenImportingModule, self).setup()
        mote.execfile = Dingus()
        self.filename = 'spec_foo.py'
        self.module = ImportedModule(self.filename)

    def should_import_file(self):
        assert mote.execfile.calls('()', self.filename, DontCare)

    def should_import_globals(self):
        assert mote.execfile.calls('()', DontCare, self.module)

    def should_be_dict(self):
        assert isinstance(self.module, dict)

