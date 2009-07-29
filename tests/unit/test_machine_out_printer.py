from dingus import Dingus, DingusTestCase, exception_raiser
import mote
from mote import MachineOutputPrinter
from tests.unit.patchedstdout import PatchedStdoutMixin


class BaseFixture(DingusTestCase(MachineOutputPrinter),
                  PatchedStdoutMixin(mote)):
    pass


class WhenCaseFails(BaseFixture):
    def setup(self):
        super(WhenCaseFails, self).setup()
        failure = Dingus(exception_line=123,
                         exception_description='exception description')
        context = Dingus(is_case=True,
                         success=False,
                         filename='filename.py',
                         failure=failure,
                         children=[])
        context.name = 'some_context'
        suite = Dingus(contexts=[context])
        MachineOutputPrinter(suite).print_result()

    def should_print_error(self):
        assert self._printed_lines() == [
            'filename.py: In some_context\n',
            'filename.py:123: error: exception description\n']


class WhenParentContextFails(BaseFixture):
    def setup(self):
        super(WhenParentContextFails, self).setup()
        context = Dingus(is_case=False,
                         success=False,
                         children=[])
        suite = Dingus(contexts=[context])
        MachineOutputPrinter(suite).print_result()

    def should_not_print_anything(self):
        assert self._printed_lines() == []


class WhenNestedCaseFails(BaseFixture):
    def setup(self):
        super(WhenNestedCaseFails, self).setup()
        failure = Dingus(exception_line=123,
                         exception_description='exception description')
        child = Dingus('child',
                       is_case=True,
                       success=False,
                       filename='filename.py',
                       failure=failure,
                       children=[])
        child.name = 'some_context'
        parent = Dingus('parent',
                        is_case=False,
                        children=[child])
        suite = Dingus(contexts=[parent])
        MachineOutputPrinter(suite).print_result()

    def should_print_error(self):
        assert self._printed_lines() == [
            'filename.py: In some_context\n',
            'filename.py:123: error: exception description\n']


class WhenContextSucceeds(BaseFixture):
    def setup(self):
        super(WhenContextSucceeds, self).setup()
        context = Dingus(success=True,
                         children=[])
        suite = Dingus(contexts=[context])
        MachineOutputPrinter(suite).print_result()

    def should_not_print_anything(self):
        assert self._printed_lines() == []

