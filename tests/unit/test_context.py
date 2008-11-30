from dingus import Dingus, DingusFixture
import mote
from mote import Context


class WhenRunningContextFromFunction(DingusFixture(Context)):
    def setup(self):
        super(WhenRunningContextFromFunction, self).setup()
        self.context_function = Dingus()
        self.case_function = Dingus()
        mote.LocalFunctions.return_value = dict(case=self.case_function)
        self.context = Context(self.context_function)
        self.context.run()

    def should_extract_spec_cases(self):
        assert mote.LocalFunctions.calls('()', self.context_function)

    def should_run_functions_in_context(self):
        assert self.case_function.calls

