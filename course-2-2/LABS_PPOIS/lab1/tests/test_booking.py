import unittest
from datetime import date, timedelta
from models.room import Room, RoomType, RoomStatus
from models.guest import Guest
from models.booking import Booking
from models.exceptions import RoomNotAvailableError


class TestBooking(unittest.TestCase):
    def setUp(self):
        self.room = Room(101, RoomType.SINGLE, 100.0)
        self.guest = Guest(1, "John Doe", "john@example.com", "1234567890", "AB1234567")
        self.check_in = date.today()
        self.check_out = date.today() + timedelta(days=3)
        self.booking = Booking(1, self.guest, self.room, self.check_in, self.check_out)

    def test_booking_initialization(self):
        self.assertEqual(self.booking.booking_id, 1)
        self.assertEqual(self.booking.guest, self.guest)
        self.assertEqual(self.booking.room, self.room)
        self.assertEqual(self.booking.check_in_date, self.check_in)
        self.assertEqual(self.booking.check_out_date, self.check_out)
        self.assertFalse(self.booking.is_paid)
        self.assertFalse(self.booking.is_cancelled)
        self.assertEqual(self.room.status, RoomStatus.OCCUPIED)
        self.assertEqual(self.guest.check_in_date, self.check_in)
        self.assertEqual(self.guest.check_out_date, self.check_out)

    def test_room_not_available(self):
        occupied_room = Room(102, RoomType.DOUBLE, 150.0)
        occupied_room.set_status(RoomStatus.OCCUPIED)

        with self.assertRaises(RoomNotAvailableError):
            Booking(2, self.guest, occupied_room, self.check_in, self.check_out)

    def test_cancel_booking(self):
        self.booking.cancel_booking()
        self.assertTrue(self.booking.is_cancelled)
        self.assertEqual(self.room.status, RoomStatus.AVAILABLE)
        self.assertIsNone(self.guest.check_in_date)
        self.assertIsNone(self.guest.check_out_date)

    def test_calculate_total(self):
        # 3 nights at $100/night = $300
        self.assertEqual(self.booking.calculate_total(), 300.0)

        # Add services
        self.guest.add_service("Breakfast", 15.0)
        self.guest.add_service("Laundry", 10.0)
        self.assertEqual(self.booking.calculate_total(), 325.0)

    def test_str_representation(self):
        booking_str = str(self.booking)
        self.assertIn("Booking 1", booking_str)
        self.assertIn("Room 101", booking_str)
        self.assertIn("John Doe", booking_str)
        self.assertIn(str(self.check_in), booking_str)
        self.assertIn(str(self.check_out), booking_str)


if __name__ == "__main__":
    unittest