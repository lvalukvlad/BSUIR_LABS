import unittest
from unittest.mock import MagicMock, patch
from guest import Guest

class TestGuest(unittest.TestCase):
    def setUp(self):
        self.guest = Guest()
        self.guest._Guest__cli_print = MagicMock()
        self.guest._Guest__booking = MagicMock()

    def test_add_guest(self):
        with patch("person.Person.add_person") as mock_add_person:
            self.guest.add_guest()
            mock_add_person.assert_called()

    def test_order_cleaning(self):
        self.guest.order_cleaning()
        self.assertTrue(self.guest._Guest__services["cleaning"])

    def test_get_services_cost(self):
        self.guest._Guest__services = {"cleaning": True, "food": False}
        self.assertEqual(self.guest.get_services_cost(), 15)

    def test_select_room(self):
        with patch.object(self.guest._Guest__booking, 'select_room') as mock_select:
            self.guest.select_room()
            mock_select.assert_called_once()

    def test_upgrade_room(self):
        with patch.object(self.guest._Guest__booking, 'upgrade_room') as mock_upgrade:
            self.guest.upgrade_room()
            mock_upgrade.assert_called_once()