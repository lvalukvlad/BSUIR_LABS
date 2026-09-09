import unittest
from models.service import Service, ServiceType
from models.exceptions import ServiceError


class TestService(unittest.TestCase):
    def setUp(self):
        self.service = Service()

    def test_initial_services(self):
        self.assertEqual(len(self.service.services), 5)
        self.assertIn(ServiceType.BREAKFAST, self.service.services)
        self.assertIn(ServiceType.LAUNDRY, self.service.services)
        self.assertIn(ServiceType.ROOM_SERVICE, self.service.services)
        self.assertIn(ServiceType.SPA, self.service.services)
        self.assertIn(ServiceType.TRANSPORT, self.service.services)

    def test_get_service_price(self):
        self.assertEqual(self.service.get_service_price(ServiceType.BREAKFAST), 15.0)
        self.assertEqual(self.service.get_service_price(ServiceType.SPA), 50.0)

    def test_get_invalid_service(self):
        with self.assertRaises(ServiceError):
            self.service.get_service_price("INVALID_SERVICE")

    def test_add_service(self):
        new_service_type = ServiceType(6)  # Assuming 6 is a new enum value
        self.service.add_service(new_service_type, 75.0)
        self.assertIn(new_service_type, self.service.services)
        self.assertEqual(self.service.services[new_service_type], 75.0)

    def test_remove_service(self):
        self.service.remove_service(ServiceType.TRANSPORT)
        self.assertNotIn(ServiceType.TRANSPORT, self.service.services)

    def test_remove_nonexistent_service(self):
        initial_count = len(self.service.services)
        self.service.remove_service("NON_EXISTENT")
        self.assertEqual(len(self.service.services), initial_count)


if __name__ == "__main__":
    unittest.main()