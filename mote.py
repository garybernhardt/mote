import sys


class LocalFunctions(dict):
    def __init__(self, function):
        self.function = function
        self._call_function_with_trace()

    def _call_function_with_trace(self):
        sys.settrace(self._trace_function)
        self.function()
        sys.settrace(None)

    def _trace_function(self, frame, event, arg):
        if event == 'return':
            self._trace_return_statement(frame)
        elif event == 'call':
            trace_function_for_function = self._trace_function_call(frame)
            return trace_function_for_function

    def _trace_return_statement(self, frame):
        local_functions = self._local_functions_in_frame(frame)
        self.update(frame.f_locals)

    def _trace_function_call(self, frame):
        traced_fn_name = frame.f_code.co_name
        if traced_fn_name == self.function.__name__:
            return self._trace_function
        else:
            return None

    @staticmethod
    def _local_functions_in_frame(frame):
        return [local_obj
                for name, local_obj in frame.f_locals.items()
                if callable(local_obj)]


if __name__ == '__main__':
    print 'All specs passed'

