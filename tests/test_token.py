import json
import os
import unittest
from io import StringIO
from unittest.mock import patch

from src import perc
from tests.shared import assert_raises, TestArgParserWithErrorRaises


class TestEmbed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.cmd_start = ['token', '-t', os.path.join(test_dir, 'tokens.json')]
        cls.parser = TestArgParserWithErrorRaises

    @patch('sys.stdout', new_callable=StringIO)
    def test_token_errors(self, _):
        assert_raises(self, perc.run, ['token'], 'token.*subcommand')

    @patch('sys.stdout', new_callable=StringIO)
    def test_get_token(self, mock_stdout):
        perc.run(self.parser, self.cmd_start + ['dump'])
        output = json.loads(mock_stdout.getvalue())
        expected = {
            'sub': '195ba25b-1b2f-4566-8f2c-04ae774cb39e',
            'email': 'cli-tester@perpetuator.com',
            'cognito:username': 'cli-tester'
        }
        self.assertEqual(output, output | expected)  # check that output contains expected
