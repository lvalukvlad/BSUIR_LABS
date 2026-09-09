from datetime import date
from room import Room, RoomStatus  # Fixed import
from guest import Guest
from exceptions import RoomNotAvailableError

class Booking:
    def __init__(self, booking_id: int, guest: Guest, room: Room,
                 check_in_date: date, check_out_date: date):
        self.booking_id = booking_id
        self.guest = guest
        self.room = room
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.is_paid = False
        self.is_cancelled = False

        if room.status != RoomStatus.AVAILABLE:  # Now RoomStatus is defined
            raise RoomNotAvailableError(f"Room {room.number} is not available")

        room.set_status(RoomStatus.OCCUPIED)
        guest.check_in_date = check_in_date
        guest.check_out_date = check_out_date

    def cancel_booking(self) -> None:
        self.is_cancelled = True
        self.room.set_status(RoomStatus.AVAILABLE)
        self.guest.check_in_date = None
        self.guest.check_out_date = None

    def calculate_total(self) -> float:
        nights = (self.check_out_date - self.check_in_date).days
        return nights * self.room.price + self.guest.calculate_services_total()

    def __str__(self) -> str:
        return (f"Booking {self.booking_id}: Room {self.room.number}, "
                f"Guest {self.guest.name}, Dates: {self.check_in_date} to {self.check_out_date}, "
                f"Total: ${self.calculate_total()}, Paid: {self.is_paid}")
        room.set_status(RoomStatus.OCCUPIED)
        guest.check_in_date = check_in_date
        guest.check_out_date = check_out_date

    def cancel_booking(self) -> None:
        self.is_cancelled = True
        self.room.set_status(RoomStatus.AVAILABLE)
        self.guest.check_in_date = None
        self.guest.check_out_date = None

    def calculate_total(self) -> float:
        nights = (self.check_out_date - self.check_in_date).days
        return nights * self.room.price + self.guest.calculate_services_total()

    def __str__(self) -> str:
        return (f"Booking {self.booking_id}: Room {self.room.number}, "
                f"Guest {self.guest.name}, Dates: {self.check_in_date} to {self.check_out_date}, "
                f"Total: ${self.calculate_total()}, Paid: {self.is_paid}")