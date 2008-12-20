from dingus import Dingus, DingusTestCase, DontCare
import mote
from mote import PythonFilesInDirectory


class BaseFixture(DingusTestCase(PythonFilesInDirectory)):
    def setup(self):
        super(BaseFixture, self).setup()
        self.root_dir = 'root'


class CasesForListingDirectoryContents:
    def should_list_directory_contents(self):
        assert mote.os.calls('listdir', self.root_dir).one()


class WhenRootIsAPythonFile(BaseFixture):
    def setup(self):
        super(WhenRootIsAPythonFile, self).setup()
        mote.os.path.isdir.return_value = False
        self.modules = PythonFilesInDirectory('foo.py')

    def should_return_python_file(self):
        assert self.modules == ['foo.py']


class WhenDirectoryIsEmpty(BaseFixture,
                           CasesForListingDirectoryContents):
    def setup(self):
        super(WhenDirectoryIsEmpty, self).setup()
        mote.os.listdir.return_value = []
        self.modules = PythonFilesInDirectory(self.root_dir)

    def should_be_empty(self):
        assert self.modules == []


class WhenDirectoryContainsSomething(BaseFixture,
                                     CasesForListingDirectoryContents):
    def setup(self):
        super(WhenDirectoryContainsSomething, self).setup()
        mote.PythonFilesInDirectory = Dingus()
        mote.PythonFilesInDirectory.return_value = ['nested_file']
        self.subdir = Dingus()
        mote.os.path.isdir = lambda path: path in (self.root_dir, self.subdir)
        mote.os.listdir.return_value = [self.subdir]
        self.modules = PythonFilesInDirectory(self.root_dir)

    def should_return_child(self):
        assert self.modules == ['nested_file']

    def should_get_subdirectories_recursively(self):
        full_subdirectory_path = mote.os.path.calls(
            'join',
            self.root_dir,
            self.subdir).one().return_value
        assert mote.PythonFilesInDirectory.calls(
            '()',full_subdirectory_path).one()

