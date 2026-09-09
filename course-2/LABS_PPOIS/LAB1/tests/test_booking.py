import unittest
from unittest.mock import MagicMock
from booking import Booking


class TestBooking(unittest.TestCase):
    def setUp(self):
        self.booking = Booking()
        self.booking._Booking__cli_print = MagicMock()  # Мок вывода в консоль

    def test_select_room(self):
        self.booking.select_room()
        self.assertGreaterEqual(self.booking.get_booking_data()["room_quality"], 20)
        self.assertLessEqual(self.booking.get_booking_data()["room_quality"], 100)

    def test_upgrade_room(self):
        self.booking.select_room()
        initial_quality = self.booking.get_booking_data()["room_quality"]
        self.booking.upgrade_room()
        self.assertGreaterEqual(
            self.booking.get_booking_data()["room_quality"], initial_quality
        )

    def test_set_price(self):
        self.booking.set_price(150)
        self.assertEqual(self.booking.get_price(), 150)

    def test_select_service(self):
        self.booking.select_service()
        quality = self.booking.get_booking_data()["service_level"]
        self.assertTrue(20 <= quality <= 100)

    def test_upgrade_service(self):
        self.booking.select_service()
        initial = self.booking.get_booking_data()["service_level"]
        self.booking.upgrade_service()
        self.assertGreaterEqual(
            self.booking.get_booking_data()["service_level"],
            initial
        )