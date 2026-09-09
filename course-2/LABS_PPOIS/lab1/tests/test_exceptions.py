import unittest
import sys
import os

# Добавляем корневую директорию проекта в путь Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.exceptions import (
    HotelException, RoomNotAvailableError, GuestNotFoundError,
    BookingNotFoundError, PaymentError, ServiceError
)


class TestExceptions(unittest.TestCase):
    def test_hotel_exception(self):
        with self.assertRaises(HotelException):
            raise HotelException("Test error")
        try:
            raise HotelException("Test message")
        except HotelException as e:
            self.assertEqual(str(e), "Test message")

    def test_room_not_available_error(self):
        with self.assertRaises(RoomNotAvailableError):
            raise RoomNotAvailableError("Room 101 is not available")
        self.assertTrue(issubclass(RoomNotAvailableError, HotelException))

    def test_guest_not_found_error(self):
        with self.assertRaises(GuestNotFoundError):
            raise GuestNotFoundError("Guest with ID 1 not found")
        self.assertTrue(issubclass(GuestNotFoundError, HotelException))

    def test_booking_not_found_error(self):
        with self.assertRaises(BookingNotFoundError):
            raise BookingNotFoundError("Booking with ID 1 not found")
        self.assertTrue(issubclass(BookingNotFoundError, HotelException))

    def test_payment_error(self):
        with self.assertRaises(PaymentError):
            raise PaymentError("Payment failed")
        self.assertTrue(issubclass(PaymentError, HotelException))

    def test_service_error(self):
        with self.assertRaises(ServiceError):
            raise ServiceError("Service not available")
        self.assertTrue(issubclass(ServiceError, HotelException))


if __name__ == "__main__":
    unittest.main()