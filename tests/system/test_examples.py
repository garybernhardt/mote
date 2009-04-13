import os


from tests.system.test_mote import SystemTest


class TestExamples(SystemTest):
    def assert_output_matches_comments(self, path):
        self.test_file_path = path
        file_contents = [line.strip() for line in file(path, 'r')]
        output_marker = file_contents.index('# Output:')
        output_lines = file_contents[output_marker + 2:]
        output_lines = [line[2:] for line in output_lines]
        output = '\n'.join(output_lines)
        output = output.replace('$ROOT', os.getcwd())
        self._assert_output_equals(output)

    def should_match_output_in_example_comments(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..',
                                                '..'))
        examples_dir = os.path.join(base_dir, 'examples')
        example_file_paths = [path
                              for path in os.listdir(examples_dir)
                              if path.endswith('.py')]

        for path in example_file_paths:
            abs_path = os.path.join(examples_dir, path)
            yield self.assert_output_matches_comments, abs_path

