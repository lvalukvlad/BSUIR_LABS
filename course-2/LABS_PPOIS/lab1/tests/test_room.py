import unittest
from models.room import Room, RoomType, RoomStatus


class TestRoom(unittest.TestCase):
    def setUp(self):
        self.room = Room(101, RoomType.SINGLE, 100.0)

    def test_room_initialization(self):
        self.assertEqual(self.room.number, 101)
        self.assertEqual(self.room.type, RoomType.SINGLE)
        self.assertEqual(self.room.price, 100.0)
        self.assertEqual(self.room.status, RoomStatus.AVAILABLE)
        self.assertEqual(len(self.room.features), 0)

    def test_add_feature(self):
        self.room.add_feature("WiFi")
        self.assertIn("WiFi", self.room.features)
        self.assertEqual(len(self.room.features), 1)

        # Test adding duplicate feature
        self.room.add_feature("WiFi")
        self.assertEqual(len(self.room.features), 1)

    def test_remove_feature(self):
        self.room.add_feature("WiFi")
        self.room.add_feature("TV")
        self.assertEqual(len(self.room.features), 2)

        self.room.remove_feature("WiFi")
        self.assertNotIn("WiFi", self.room.features)
        self.assertIn("TV", self.room.features)
        self.assertEqual(len(self.room.features), 1)

        # Test removing non-existent feature
        self.room.remove_feature("MiniBar")
        self.assertEqual(len(self.room.features), 1)

    def test_set_status(self):
        self.room.set_status(RoomStatus.OCCUPIED)
        self.assertEqual(self.room.status, RoomStatus.OCCUPIED)

        self.room.set_status(RoomStatus.MAINTENANCE)
        self.assertEqual(self.room.status, RoomStatus.MAINTENANCE)

        self.room.set_status(RoomStatus.AVAILABLE)
        self.assertEqual(self.room.status, RoomStatus.AVAILABLE)

    def test_str_representation(self):
        room_str = str(self.room)
        self.assertIn("Room 101", room_str)
        self.assertIn("SINGLE", room_str)
        self.assertIn("$100.0", room_str)
        self.assertIn("AVAILABLE", room_str)


if __name__ == "__main__":
    unittest.main()