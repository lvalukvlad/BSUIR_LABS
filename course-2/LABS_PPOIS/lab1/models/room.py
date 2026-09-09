from enum import Enum, auto
from typing import Optional


class RoomType(Enum):
    SINGLE = auto()
    DOUBLE = auto()
    SUITE = auto()
    DELUXE = auto()


class RoomStatus(Enum):
    AVAILABLE = auto()
    OCCUPIED = auto()
    MAINTENANCE = auto()


class Room:
    def __init__(self, number: int, room_type: RoomType, price: float, status: RoomStatus = RoomStatus.AVAILABLE):
        self.number = number
        self.type = room_type
        self.price = price
        self.status = status
        self.features: list[str] = []

    def add_feature(self, feature: str) -> None:
        if feature not in self.features:
            self.features.append(feature)

    def remove_feature(self, feature: str) -> None:
        if feature in self.features:
            self.features.remove(feature)

    def set_status(self, status: RoomStatus) -> None:
        self.status = status

    def __str__(self) -> str:
        return f"Room {self.number} - {self.type.name} (${self.price}/night), Status: {self.status.name}"