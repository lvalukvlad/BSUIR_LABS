import unittest
from models.staff import Staff, StaffRole


class TestStaff(unittest.TestCase):
    def setUp(self):
        self.staff = Staff(1, "John Doe", StaffRole.RECEPTIONIST, "john@hotel.com")

    def test_staff_initialization(self):
        self.assertEqual(self.staff.staff_id, 1)
        self.assertEqual(self.staff.name, "John Doe")
        self.assertEqual(self.staff.role, StaffRole.RECEPTIONIST)
        self.assertEqual(self.staff.contact, "john@hotel.com")

    def test_different_roles(self):
        chef = Staff(2, "Gordon Ramsay", StaffRole.CHEF, "gordon@hotel.com")
        self.assertEqual(chef.role, StaffRole.CHEF)

        manager = Staff(3, "Manager", StaffRole.MANAGER, "manager@hotel.com")
        self.assertEqual(manager.role, StaffRole.MANAGER)

    def test_str_representation(self):
        staff_str = str(self.staff)
        self.assertIn("Staff 1", staff_str)
        self.assertIn("John Doe", staff_str)
        self.assertIn("RECEPTIONIST", staff_str)
        self.assertIn("john@hotel.com", staff_str)


if __name__ == "__main__":
    unittest.main()