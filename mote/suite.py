import sys
from os.path import dirname, abspath
import re
import traceback
from mote.localfunctions import LocalFunctions


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


class Context:
    def __init__(self, context_function, parent=None):
        self.original_context_function = context_function
        self.parent = parent
        self.name = context_function.__name__
        self.filename = self._function_filename()

        self.children = self._collect_children()
        if self.success and self.children:
            self.success = all(child.success for child in self.children)

    def _function_filename(self):
        return self.original_context_function.func_code.co_filename

    @property
    def is_case(self):
        return not self.children

    @property
    def has_cases(self):
        return self.children and any(child
                                     for child in self.children
                                     if child.is_case)

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


class Failure:
    def __init__(self, exc_info):
        self.exc_type, self.exc_value, exc_traceback = exc_info
        self.exc_traceback = self._remove_mote_from_traceback(exc_traceback)
        self.exception_line = self.exc_traceback.tb_lineno
        self.exc_info = exc_info

    @property
    def formatted_exception(self):
        traceback_lines = traceback.format_exception(self.exc_type,
                                                     self.exc_value,
                                                     self.exc_traceback)
        return ''.join(traceback_lines)

    def _remove_mote_from_traceback(self, traceback):
        mote_dir = dirname(abspath(__file__))
        while True:
            frame = traceback.tb_frame
            code = frame.f_code
            filename = code.co_filename
            code_dir = dirname(abspath(filename))
            if code_dir != mote_dir:
                break
            else:
                traceback = traceback.tb_next

        return traceback

    @property
    def exception_description(self):
        desc = traceback.format_exception_only(self.exc_type, self.exc_value)
        return self._short_exception_description(desc)

    def _short_exception_description(self, exception_description_lines):
        return exception_description_lines[-1].strip()

