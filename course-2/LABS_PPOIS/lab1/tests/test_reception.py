import unittest
from datetime import date, timedelta
from models.room import Room, RoomType, RoomStatus
from models.guest import Guest
from models.staff import Staff, StaffRole
from models.reception import Reception
from models.booking import Booking
from models.exceptions import (
    RoomNotAvailableError,
    GuestNotFoundError,
    BookingNotFoundError
)
class TestReception(unittest.TestCase):
    def setUp(self):
        self.reception = Reception()
        self.room = Room(101, RoomType.SINGLE, 100.0)
        self.reception.add_room(self.room)
        self.guest = self.reception.register_guest(
            "John Doe", "john@example.com", "1234567890", "AB1234567"
        )
        self.staff = Staff(1, "Receptionist", StaffRole.RECEPTIONIST, "reception@hotel.com")
        self.reception.add_staff(self.staff)
    
    def test_add_room(self):
        self.assertIn(self.room.number, self.reception.rooms)
        self.assertEqual(self.reception.rooms[self.room.number], self.room)
    
    def test_add_staff(self):
        self.assertIn(self.staff.staff_id, self.reception.staff)
        self.assertEqual(self.reception.staff[self.staff.staff_id], self.staff)
    
    def test_register_guest(self):
        self.assertIn(self.guest.guest_id, self.reception.guests)
        self.assertEqual(self.reception.guests[self.guest.guest_id], self.guest)
        self.assertEqual(self.reception.next_guest_id, 2)
    
    def test_book_room(self):
        check_in = date.today().isoformat()
        check_out = (date.today() + timedelta(days=3)).isoformat()
        booking = self.reception.book_room(
            self.guest.guest_id, self.room.number, check_in, check_out
        )
        
        self.assertIn(booking.booking_id, self.reception.bookings)
        self.assertEqual(self.reception.next_booking_id, 2)
        self.assertEqual(booking.guest, self.guest)
        self.assertEqual(booking.room, self.room)
    
    def test_book_room_invalid_guest(self):
        with self.assertRaises(GuestNotFoundError):
            self.reception.book_room(999, self.room.number, "2023-12-01", "2023-12-05")
    
    def test_book_room_invalid_room(self):
        with self.assertRaises(KeyError):
            self.reception.book_room(self.guest.guest_id, 999, "2023-12-01", "2023-12-05")
    
    def test_check_out(self):
        booking = self.reception.book_room(
            self.guest.guest_id, self.room.number, 
            "2023-12-01", "2023-12-05"
        )
        total = self.reception.check_out(booking.booking_id)
        
        self.assertEqual(total, 400.0)  # 4 nights * $100
        self.assertTrue(booking.is_paid)
        self.assertEqual(self.room.status, RoomStatus.AVAILABLE)
    
    def test_check_out_invalid_booking(self):
        with self.assertRaises(BookingNotFoundError):
            self.reception.check_out(999)
    
    def test_get_available_rooms(self):
        available_rooms = self.reception.get_available_rooms()
        self.assertEqual(len(available_rooms), 1)
        self.assertEqual(available_rooms[0], self.room)
        
        # Book the room
        self.reception.book_room(
            self.guest.guest_id, self.room.number, 
            "2023-12-01", "2023-12-05"
        )
        available_rooms = self.reception.get_available_rooms()
        self.assertEqual(len(available_rooms), 0)

if __name__ == "__main__":
    unittest.main()