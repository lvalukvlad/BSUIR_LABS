import unittest
from unittest.mock import MagicMock, patch
from staff import Staff

class TestStaff(unittest.TestCase):
    def setUp(self):
        self.staff = Staff()
        self.staff._Staff__cli_print = MagicMock()

    def test_add_staff(self):
        with patch("person.Person.add_person") as mock_add_person:
            self.staff.add_staff()
            mock_add_person.assert_called()

    def test_confirm_booking(self):
        self.assertTrue(
            self.staff.confirm_booking({"room_quality": 80, "service_level": 90})
        )
        self.assertFalse(
            self.staff.confirm_booking({"room_quality": 60, "service_level": 90})
        )
        self.assertFalse(
            self.staff.confirm_booking({"room_quality": 80, "service_level": 70})
        )

    def test_get_service_quality(self):
        self.staff._Staff__service_quality = 85
        self.assertEqual(self.staff.get_service_quality(), 85)

    def test_get_first_name(self):
        self.staff._first_name = "Иван"
        self.assertEqual(self.staff.get_first_name(), "Иван")