import os
import unittest
from optparse import OptionParser
import sys
from itertools import chain

from mote.suite import SpecSuite
from mote import printers

from dingus import Dingus, DingusTestCase, DontCare, exception_raiser


class DummyTestCase(unittest.TestCase):
    def nop(self):
        pass


def raises(exception, callable_, *args, **kwargs):
    try:
        assert_raises = DummyTestCase('nop').failUnlessRaises
        assert_raises(exception, callable_, *args, **kwargs)
    except AssertionError:
        return False
    else:
        return True


# XXX: Replace this!
#   1) It was not TDDed
#   2) It doesn't clean up after itself, leaving the module broken
def isolate(object_under_test, exclude=[]):
    def decorator(fn):
        def new_fn(*args, **kwargs):
            DingusTestCase(object_under_test, exclude=exclude)().setup()
            return fn(*args, **kwargs)
        new_fn.__name__ = fn.__name__
        return new_fn
    return decorator


DEFAULT_GLOBALS = dict(raises=raises,
                       isolate=isolate,
                       Dingus=Dingus,
                       DontCare=DontCare,
                       exception_raiser=exception_raiser)


class ImportedModule(dict):
    def __init__(self, filename):
        self.update(DEFAULT_GLOBALS)
        execfile(filename, self)


class PythonFilesInDirectory(list):
    def __init__(self, parent):
        if not os.path.isdir(parent):
            self._extend_with_file(parent)
        else:
            self._extend_with_directory(parent)

    def _extend_with_file(self, path):
        if path.endswith('.py'):
            self.append(path)

    def _extend_with_directory(self, path):
        for child in os.listdir(path):
            child_path = os.path.join(path, child)
            self.extend(PythonFilesInDirectory(child_path))

def main():
    parser = OptionParser()
    parser.add_option('-q', '--quiet',
                      action='store_const',
                      dest='output_type',
                      const='quiet',
                      default='spec')
    parser.add_option('--machine-out',
                      action='store_const',
                      dest='output_type',
                      const='machine')
    options, args = parser.parse_args()

    printer_classes = {'quiet': printers.QuietPrinter,
                       'spec': printers.SpecOutputPrinter,
                       'machine': printers.MachineOutputPrinter}
    printer_class = printer_classes[options.output_type]
    printer = printer_class()

    try:
        paths = list(chain(*[PythonFilesInDirectory(path) for path in args]))
        modules = map(ImportedModule, paths)
    except Exception, e:
        printer.handle_import_failure(sys.exc_info())
    else:
        suite = SpecSuite(modules)
        printer.print_suite(suite)

if __name__ == '__main__':
    main()

