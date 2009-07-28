def PatchedStdoutMixin(mote_module):
    class _PatchedStdoutMixin(object):
        def _wrote(self, text):
            return mote_module.sys.stdout.calls('write', text).one()

        def _printed_lines(self):
            return [call.args[0]
                    for call in mote_module.sys.stdout.calls('write')]
    return _PatchedStdoutMixin

