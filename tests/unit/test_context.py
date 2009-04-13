from dingus import Dingus, DingusTestCase, exception_raiser
import mote
from mote import Context


class BaseFixture(DingusTestCase(Context, 're')):
    def setup(self):
        super(BaseFixture, self).setup()

        # Replace the Context class with a Dingus because it instantiates
        # child contexts
        mote.Context = Dingus()

    def _run_context_with_case_function(self, case_function):
        self.context_function = Dingus()
        self.context_function.__name__ = 'describe_something'
        mote.LocalFunctions.case_functions.return_value = [self.case_function]
        self.context = Context(self.context_function)


class WhenRunningContextFromFunction(BaseFixture):
    def setup(self):
        super(WhenRunningContextFromFunction, self).setup()
        self.case_function = Dingus()
        self._run_context_with_case_function(self.case_function)

    def should_extract_spec_cases(self):
        assert mote.LocalFunctions.calls('case_functions',
                                         self.context_function)

    def should_take_name_from_function(self):
        assert self.context.name == 'describe_something'

    def should_have_pretty_name(self):
        assert self.context.pretty_name == 'something'


class WhenRunningMultipleCases(BaseFixture):
    def setup(self):
        super(WhenRunningMultipleCases, self).setup()
        self.context_function = Dingus()
        self.case_functions = [Dingus(), Dingus()]
        mote.LocalFunctions.case_functions.return_value = self.case_functions
        self.context = Context(self.context_function)

    def should_create_cases(self):
        assert all(mote.Case.calls('()',
                                   self.context,
                                   case_function.__name__).one()
                   for case_function in self.case_functions)

    def should_return_correct_number_of_cases(self):
        assert len(self.context.cases) == len(self.case_functions)


class WhenContextsAreNested(BaseFixture):
    def setup(self):
        super(WhenContextsAreNested, self).setup()

        def when_frobbing(): pass
        self.when_frobbing = when_frobbing

        mote.LocalFunctions.context_functions.return_value = [when_frobbing]
        self.context_function = Dingus()
        self.context = Context(self.context_function)

    def should_create_context(self):
        assert mote.Context.calls('()',
                                  self.when_frobbing,
                                  self.context).one()

    def should_collect_contexts(self):
        assert self.context.contexts == [mote.Context.return_value]

    def should_extract_context_functions(self):
        assert mote.LocalFunctions.calls('context_functions',
                                         self.context_function).one()

    def should_use_child_context_function_to_create_child_context(self):
        inner_context_function = mote.Context.calls('()').one().args[0]
        assert inner_context_function.__name__ == 'when_frobbing'


class WhenCasesFail(BaseFixture):
    def setup(self):
        super(WhenCasesFail, self).setup()
        mote.LocalFunctions.return_value = [Dingus()]
        mote.Case.return_value = Dingus(success=False)
        self.context = Context(Dingus())

    def should_indicate_failure(self):
        assert not self.context.success


class WhenNestedContextsFail(BaseFixture):
    def setup(self):
        super(WhenNestedContextsFail, self).setup()
        mote.LocalFunctions.return_value = [Dingus()]
        mote.Context.return_value = Dingus(success=False)
        self.context = Context(Dingus())

    def should_indicate_failure(self):
        assert not self.context.success


class WhenCasesAndNestedContextsPass(BaseFixture):
    def setup(self):
        super(WhenCasesAndNestedContextsPass, self).setup()
        mote.LocalFunctions.return_value = [Dingus()]
        mote.Case.return_value = Dingus(success=True)
        mote.Context.return_value = Dingus(success=True)
        self.context = Context(Dingus())

    def should_indicate_success(self):
        assert self.context.success


class WhenGettingFreshFunctions(BaseFixture):
    def setup(self):
        super(WhenGettingFreshFunctions, self).setup()
        self.context_function = Dingus()
        context = Context(self.context_function)
        self.fresh_function = context.fresh_function_named('child_fn')

    def should_extract_function_from_context_locals(self):
        assert mote.LocalFunctions.calls('()', self.context_function).one()

    def should_return_function_with_requested_name(self):
        local_functions = mote.LocalFunctions.return_value
        fresh_function = local_functions.calls('function_with_name',
                                               'child_fn').one().return_value
        assert self.fresh_function is fresh_function


class WhenContextHasParent(BaseFixture):
    def setup(self):
        super(WhenContextHasParent, self).setup()
        mote.LocalFunctions.return_value = [Dingus()]
        self.context_function, self.parent = Dingus.many(2)
        self.context = Context(self.context_function, self.parent)

    def should_get_context_function_from_parent(self):
        fresh_context_function = self.parent.calls(
            'fresh_function_named',
            self.context_function.__name__)[0].return_value
        assert self.context.context_function is fresh_context_function

