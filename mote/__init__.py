import os
import unittest
from optparse import OptionParser
import sys
from itertools import chain, count
import re
import traceback

from mote.localfunctions import LocalFunctions
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
def isolate(object_under_test, *exclusions):
    def decorator(fn):
        def new_fn(*args, **kwargs):
            DingusTestCase(object_under_test, *exclusions)().setup()
            return fn(*args, **kwargs)
        new_fn.__name__ = fn.__name__
        return new_fn
    return decorator


DEFAULT_GLOBALS = dict(raises=raises,
                       isolate=isolate,
                       Dingus=Dingus,
                       DontCare=DontCare,
                       exception_raiser=exception_raiser)


class SpecSuite:
    def __init__(self, contents_of_modules):
        self.contexts = [
            ctx
            for module_contents in contents_of_modules
            for ctx in self._contexts_from_module(module_contents.values())]
        self.success = all(ctx.success for ctx in self.contexts)

    def _contexts_from_module(self, module_contents):
        return [Context(value)
                for value in module_contents
                if callable(value)
                and value.__name__.startswith('describe_')]


class ImportedModule(dict):
    def __init__(self, filename):
        self.update(DEFAULT_GLOBALS)
        execfile(filename, self)


class Failure:
    def __init__(self, exc_info):
        self.exc_type, self.exc_value, self.exc_traceback = exc_info
        mote_dir = os.path.dirname(os.path.abspath(__file__))
        tb_level = self.exc_traceback
        while tb_level:
            tb_level_dir = os.path.abspath(tb_level.tb_frame.f_code.co_filename)
            if not tb_level_dir.startswith(mote_dir):
                break
            else:
                tb_level = tb_level.tb_next
        self.tb_level = tb_level
        self.exception_line = tb_level.tb_lineno

    def format_exception(self):
        traceback_lines = traceback.format_exception(
            self.exc_type,
            self.exc_value,
            self.tb_level)
        return '\n%s\n' % ''.join(traceback_lines)


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

class Context:
    def __init__(self, context_function, parent=None):
        self.original_context_function = context_function
        self.parent = parent
        self.name = context_function.__name__
        self.children = self._collect_children()
        if self.success and self.children:
            self.success = all(child.success for child in self.children)

    @property
    def has_cases(self):
        return self.children and any(child
                                     for child in self.children
                                     if not child.children)

    @property
    def pretty_name(self):
        if self.children:
            return self._pretty_name_with_children
        else:
            return self._pretty_name_without_children

    @property
    def _pretty_name_with_children(self):
        name = self._pretty_name_without_children
        if self.parent is not None:
            name = '%s %s' % (self.parent.pretty_name, name)
        return name

    @property
    def _pretty_name_without_children(self):
        name = self.name.replace('_', ' ')
        return re.sub('^describe ', '', name)

    @property
    def context_function(self):
        if self.parent:
            return self.parent.fresh_function_named(self.name)
        else:
            return self.original_context_function

    def fresh_function_named(self, name):
        local_functions = LocalFunctions(self.context_function)
        return local_functions.function_with_name(name)

    def _collect_children(self):
        try:
            local_functions = LocalFunctions(self.context_function)
        except Exception, e:
            self.failure = Failure(sys.exc_info())
            self.success = False
            self.exception = e
        else:
            self.success = True
            return [Context(function, self) for function in local_functions]


class SpecOutputPrinter:
    INDENT = ' ' * 2

    def __init__(self, contexts):
        self._print_contexts(contexts)

    def _failing_context_status(self, context):
        exception_name = context.exception.__class__.__name__
        failure = context.failure
        return ' -> FAIL (%s @ %i)' % (exception_name,
                                       failure.exception_line)

    def _print_case(self, context):
        failure_numbers = count(1)

        if context.success:
            result = ''
        else:
            context.failure.number = failure_numbers.next()
            result = self._failing_context_status(context)

        sys.stdout.write('%s- %s%s\n' % (self.INDENT,
                                         context.pretty_name,
                                         result))

        if not context.success:
            sys.stdout.write(context.failure.format_exception())

    def _print_contexts(self, contexts):
        for context in contexts:
            if context.has_cases:
                sys.stdout.write('%s\n' % context.pretty_name)

            if context.children:
                self._print_contexts(context.children)
            else:
                self._print_case(context)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-q', '--quiet', action='store_true', dest='quiet')
    options, args = parser.parse_args()

    paths = list(chain(*[PythonFilesInDirectory(path) for path in args]))
    modules = map(ImportedModule, paths)
    suite = SpecSuite(modules)

    if not options.quiet:
        SpecOutputPrinter(suite.contexts)

    if suite.success:
        print 'All specs passed'
    else:
        print 'Specs failed'

