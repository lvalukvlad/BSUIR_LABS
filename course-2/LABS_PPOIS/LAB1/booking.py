import random
from typing import TypedDict
from cli_print import CliPrint

class BookingDict(TypedDict):
    room_quality: int
    service_level: int

class Booking:
    __room_quality: int = 0
    __service_level: int = 0
    __total_price: int = 0
    __cli_print: CliPrint = CliPrint()

    def select_room(self):
        self.__room_quality = 20 + random.randrange(1, 80, 1)
        self.__cli_print.print(f'Качество номера: {self.__room_quality}%')

    def select_service(self):
        self.__service_level = 20 + random.randrange(1, 80, 1)
        self.__cli_print.print(f'Уровень сервиса: {self.__service_level}%')

    def upgrade_room(self):
        self.__room_quality += random.randrange(1, 30, 1)
        if self.__room_quality > 100:
            self.__room_quality = 100
        self.__cli_print.print(f'Новый уровень номера: {self.__room_quality}%')

    def upgrade_service(self):
        self.__service_level += random.randrange(1, 30, 1)
        if self.__service_level > 100:
            self.__service_level = 100
        self.__cli_print.print(f'Новый уровень сервиса: {self.__service_level}%')

    def get_booking_data(self) -> BookingDict:
        return {'room_quality': self.__room_quality, 'service_level': self.__service_level}

    def set_price(self, price: int):
        self.__total_price = price

    def get_price(self) -> int:
        return self.__total_price