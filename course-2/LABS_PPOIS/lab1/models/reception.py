from typing import List, Dict, Optional
from booking import Booking
from guest import Guest
from room import Room
from staff import Staff
from exceptions import GuestNotFoundError, BookingNotFoundError


class Reception:
    def __init__(self):
        self.bookings: Dict[int, Booking] = {}
        self.guests: Dict[int, Guest] = {}
        self.rooms: Dict[int, Room] = {}
        self.staff: Dict[int, Staff] = {}
        self.next_booking_id = 1
        self.next_guest_id = 1

    def add_room(self, room: Room) -> None:
        self.rooms[room.number] = room

    def add_staff(self, staff: Staff) -> None:
        self.staff[staff.staff_id] = staff

    def register_guest(self, name: str, email: str, phone: str, passport: str) -> Guest:
        guest = Guest(self.next_guest_id, name, email, phone, passport)
        self.guests[guest.guest_id] = guest
        self.next_guest_id += 1
        return guest

    def book_room(self, guest_id: int, room_number: int,
                  check_in_date: str, check_out_date: str) -> Booking:
        if guest_id not in self.guests:
            raise GuestNotFoundError(f"Guest with ID {guest_id} not found")

        if room_number not in self.rooms:
            raise KeyError(f"Room {room_number} does not exist")

        from datetime import datetime
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()

        booking = Booking(
            self.next_booking_id,
            self.guests[guest_id],
            self.rooms[room_number],
            check_in,
            check_out
        )

        self.bookings[booking.booking_id] = booking
        self.next_booking_id += 1
        return booking

    def check_out(self, booking_id: int) -> float:
        if booking_id not in self.bookings:
            raise BookingNotFoundError(f"Booking with ID {booking_id} not found")

        booking = self.bookings[booking_id]
        total = booking.calculate_total()
        booking.is_paid = True
        booking.room.set_status(RoomStatus.AVAILABLE)
        booking.guest.check_in_date = None
        booking.guest.check_out_date = None

        return total

    def get_available_rooms(self) -> List[Room]:
        return [room for room in self.rooms.values() if room.status == RoomStatus.AVAILABLE]