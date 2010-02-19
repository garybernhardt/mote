import os
from optparse import OptionParser
import sys
from itertools import chain

from mote.suite import SpecSuite
from mote import printers


def globals_from_execed_file(filename):
    globals_ = {}
    execfile(filename, globals_)
    return globals_


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
        modules = map(globals_from_execed_file, paths)
    except Exception, e:
        printer.handle_import_failure(sys.exc_info())
    else:
        suite = SpecSuite(modules)
        printer.print_suite(suite)

if __name__ == '__main__':
    main()

