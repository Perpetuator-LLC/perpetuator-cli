import os
import unittest
from io import StringIO
from unittest.mock import patch

from src import perc
from tests.shared import assert_raises, TestArgParserWithErrorRaises


class TestCollections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.cmd_start = ['post-index', '-t', os.path.join(test_dir, 'tokens.json')]
        cls.parser = TestArgParserWithErrorRaises

    def test_prompt_errors(self):
        assert_raises(self, perc.run, ['prompt'])

    @patch('sys.stdout', new_callable=StringIO)
    def test_prompt(self, mock_stdout):
        name = 'create_test'  # self._testMethodName
        perc.run(self.parser, self.cmd_start + [name, "reply with: WORKING"])
        self.assertRegex(mock_stdout.getvalue(), ".*answer.*WORKING.*")

    @patch('sys.stdout', new_callable=StringIO)
    def test_chat_prompt(self, mock_stdout):
        name = 'create_test'  # self._testMethodName
        perc.run(self.parser, self.cmd_start + ["--chat", name, "If you understand this, then you will only reply "
                                                                 "with: WORKING"])
        self.assertRegex(mock_stdout.getvalue(), ".*answer.*WORKING.*")
