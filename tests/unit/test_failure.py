from dingus import Dingus, DingusTestCase, exception_raiser, DontCare
import mote as mod
from mote import Failure


class DescribeFailure(DingusTestCase(Failure)):
    def setup(self):
        super(DescribeFailure, self).setup()
        exc_info = Dingus.many(3)
        self.exc_type, self.exc_value, self.tb = exc_info
        mod.traceback.format_exception.return_value = ['tb-line-1',
                                                       'tb-line-2']
        self.failure = Failure(exc_info)

    def should_have_traceback_line_number(self):
        assert self.failure.exception_line is self.tb.tb_next.tb_lineno

    def should_format_exception(self):
        self.failure.format_exception()
        traceback_start = self.tb.tb_next
        assert mod.traceback.calls('format_exception',
                                   self.exc_type,
                                   self.exc_value,
                                   traceback_start).one()

    def should_return_formatted_exception(self):
        formatted_exception = mod.traceback.format_exception.return_value
        assert self.failure.format_exception() == '\ntb-line-1tb-line-2\n'

