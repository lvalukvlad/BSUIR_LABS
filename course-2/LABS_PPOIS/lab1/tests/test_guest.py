import unittest
from datetime import date
from models.guest import Guest


class TestGuest(unittest.TestCase):
    def setUp(self):
        self.guest = Guest(1, "John Doe", "john@example.com", "1234567890", "AB1234567")

    def test_guest_initialization(self):
        self.assertEqual(self.guest.guest_id, 1)
        self.assertEqual(self.guest.name, "John Doe")
        self.assertEqual(self.guest.email, "john@example.com")
        self.assertEqual(self.guest.phone, "1234567890")
        self.assertEqual(self.guest.passport, "AB1234567")
        self.assertIsNone(self.guest.check_in_date)
        self.assertIsNone(self.guest.check_out_date)
        self.assertEqual(len(self.guest.services_used), 0)

    def test_add_service(self):
        self.guest.add_service("Breakfast", 15.0)
        self.assertEqual(len(self.guest.services_used), 1)
        self.assertEqual(self.guest.services_used[0]["name"], "Breakfast")
        self.assertEqual(self.guest.services_used[0]["price"], 15.0)

        self.guest.add_service("Laundry", 10.0)
        self.assertEqual(len(self.guest.services_used), 2)

    def test_calculate_services_total(self):
        self.assertEqual(self.guest.calculate_services_total(), 0.0)

        self.guest.add_service("Breakfast", 15.0)
        self.assertEqual(self.guest.calculate_services_total(), 15.0)

        self.guest.add_service("Laundry", 10.0)
        self.assertEqual(self.guest.calculate_services_total(), 25.0)

    def test_dates_assignment(self):
        test_date = date(2023, 12, 1)
        self.guest.check_in_date = test_date
        self.guest.check_out_date = test_date

        self.assertEqual(self.guest.check_in_date, test_date)
        self.assertEqual(self.guest.check_out_date, test_date)

    def test_str_representation(self):
        guest_str = str(self.guest)
        self.assertIn("Guest 1", guest_str)
        self.assertIn("John Doe", guest_str)
        self.assertIn("john@example.com", guest_str)
        self.assertIn("1234567890", guest_str)


if __name__ == "__main__":
    unittest.main()