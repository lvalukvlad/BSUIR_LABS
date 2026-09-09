import unittest
from unittest.mock import MagicMock
from reception import Reception
from staff import Staff


class TestReception(unittest.TestCase):
    def setUp(self):
        self.reception = Reception()
        self.staff_mock = MagicMock(spec=Staff)
        self.reception._Reception__staff = [self.staff_mock]

    def test_add_staff(self):
        with unittest.mock.patch("staff.Staff.add_staff") as mock_add_staff:
            self.reception.add_staff()
            mock_add_staff.assert_called()

    def test_is_ready(self):
        self.reception._Reception__staff = [MagicMock(), MagicMock(), MagicMock()]
        self.assertTrue(self.reception.is_ready())

    def test_check_service_quality(self):
        self.assertTrue(
            self.reception.check_service_quality(
                {"room_quality": 85, "service_level": 90}
            )
        )
        # Тест с плохим качеством номера
        self.assertFalse(
            self.reception.check_service_quality(
                {"room_quality": 70, "service_level": 90}
            )
        )