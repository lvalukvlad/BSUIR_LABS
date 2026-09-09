from typing import TypedDict
from person import Person
from cli_print import CliPrint
import random


class BookingDict(TypedDict):
    room_quality: int
    service_level: int


class Staff(Person):
    __cli_print: CliPrint = CliPrint()
    __service_quality: int = 0

    def add_staff(self):
        self.add_person()
        self.__service_quality = random.randrange(80, 100, 1)
        self.__cli_print.print(f"Администратор {self._last_name} {self._first_name} {self._surname} добавлен!"
                              f" (Качество сервиса: {self.__service_quality}%)")

    def confirm_booking(self, booking: BookingDict) -> bool:
        if booking['room_quality'] < 70:
            self.__cli_print.print(f"Номер не соответствует стандартам ({booking['room_quality']}%)")
            return False
        if booking['service_level'] < 80:
            self.__cli_print.print(f"Услуги недостаточного уровня ({booking['service_level']}%)")
            return False
        self.__cli_print.print('Бронирование подтверждено!')
        return True

    def get_service_quality(self) -> int:
        return self.__service_quality

    def get_first_name(self) -> str:
        return self._first_name

    def is_exist(self) -> bool:
        return bool(self._surname)
