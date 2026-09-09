import unittest
from unittest.mock import MagicMock
from person import Person

class TestPerson(unittest.TestCase):
    def setUp(self):
        self.person = Person()
        self.person._Person__cli_input = MagicMock()
        self.person._Person__cli_print = MagicMock()

    def test_valid_name_input(self):
        self.person._Person__cli_input.get_input.return_value = "Иванов"
        result = self.person._get_valid_input("Фамилия")
        self.assertEqual(result, "Иванов")

    def test_invalid_name_input(self):
        self.person._Person__cli_input.get_input.side_effect = ["", "Ив", "Иванов"]
        self.person._get_valid_input("Фамилия")
        self.person._Person__cli_print.print.assert_called()