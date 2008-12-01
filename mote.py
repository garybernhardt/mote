import sys


class LocalFunctions(dict):
    def __init__(self, function):
        self.function = function
        self._call_function_with_trace()

    def _call_function_with_trace(self):
        sys.settrace(self._trace)
        self.function()
        sys.settrace(None)

    def _trace(self, frame, event, arg):
        if event == 'return':
            self._trace_return_statement(frame)
        elif event == 'call':
            trace_function_for_function = self._trace_function_call(frame)
            return trace_function_for_function

    def _trace_return_statement(self, frame):
        local_functions = self._local_functions_in_frame(frame)
        self.update(local_functions)

    def _trace_function_call(self, frame):
        traced_fn_name = frame.f_code.co_name
        if traced_fn_name == self.function.__name__:
            return self._trace
        else:
            return None

    @staticmethod
    def _local_functions_in_frame(frame):
        return dict((name, local_obj)
                    for name, local_obj in frame.f_locals.items()
                    if callable(local_obj))


class SpecSuite:
    def __init__(self, module_path):
        self.function = function

    @property
    def local_objects(self):
        function_locals = dict()
        def trace(frame, event, arg):
            traced_fn_name = frame.f_code.co_name
            if event == 'return':
                function_locals[traced_fn_name] = frame.f_locals
            elif event == 'call':
                if traced_fn_name == self.function.__name__:
                    return trace

        sys.settrace(trace)
        self.function()
        sys.settrace(None)

        return function_locals[self.function.__name__]

    def run(self):
        name = self.function.__name__
        for name, child in self.sorted_children:
            Case(child).run()


class SpecSuite:
    def __init__(self, module_path):
        self.module_path = module_path

    def run(self):
        module_contents = ImportedModule(self.module_path)
        self._run_cases(module_contents)

    def _run_cases(self, module_contents):
        for module_attribute in module_contents.values():
            if callable(module_attribute):
                Context(module_attribute).run()


class ImportedModule(dict):
    def __init__(self, filename):
        execfile(filename, self)


class Context:
    def __init__(self, context_function):
        self.context_function = context_function

    def run(self):
        case_functions = LocalFunctions(self.context_function)
        for case_function in case_functions.values():
            case_function()


if __name__ == '__main__':
    try:
        SpecSuite(sys.argv[1]).run()
    except:
        print 'Specs failed'
    else:
        print 'All specs passed'

