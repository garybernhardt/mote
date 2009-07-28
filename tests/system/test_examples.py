import os
from glob import glob
import re


from tests.system.test_mote import SystemTest


class TestExamples(SystemTest):
    def assert_output_matches_comments(self, path):
        self.test_file_path = path
        contents = [line.strip() for line in file(path, 'r')]
        expected_output = self._expected_output_from_file_contents(contents)
        self._assert_output_equals(expected_output)

    def _expected_output_from_file_contents(self, contents):
        output_marker = contents.index('# Output:')
        output_lines_with_comments = contents[output_marker + 2:]
        output_lines = [re.sub('# ?', '', line)
                        for line in output_lines_with_comments]
        raw_output = '\n'.join(output_lines)
        output = raw_output.replace('$ROOT', os.getcwd())
        return output

    def should_match_output_in_example_comments(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..',
                                                '..'))

        example_file_paths = (glob('examples/*_spec.py') +
                              glob('examples/**/*_spec.py'))

        for path in example_file_paths:
            if not os.path.basename(path) == '__init__.py':
                abs_path = os.path.join(base_dir, path)
                yield self.assert_output_matches_comments, abs_path

