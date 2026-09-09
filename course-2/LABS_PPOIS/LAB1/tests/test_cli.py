import unittest
from unittest.mock import patch
from cli_input import CliInput
from cli_print import CliPrint

class TestCliInput(unittest.TestCase):
    def test_set_input(self):
        cli_input = CliInput()
        with patch("builtins.input", return_value="test"):
            cli_input.set_input("Ввод: ")
            self.assertEqual(cli_input.get_input(), "test")

class TestCliPrint(unittest.TestCase):
    def test_print(self):
        cli_print = CliPrint()
        with patch("builtins.print") as mock_print:
            cli_print.print("Hello")
            mock_print.assert_called_with("Hello")