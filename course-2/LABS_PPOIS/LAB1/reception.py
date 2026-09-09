import time
from staff import Staff
from typing import TypedDict, List
from cli_print import CliPrint


class BookingDict(TypedDict):
    room_quality: int
    service_level: int


class Reception:
    __staff: List[Staff] = []
    __required_service_level: int = 80
    __cli_print: CliPrint = CliPrint()

    def add_staff(self):
        if len(self.__staff) >= 3:
            self.__cli_print.print("Достигнут максимальный размер персонала (3 человека)!")
            return

        employee = Staff()
        employee.add_staff()
        self.__staff.append(employee)
        self.__cli_print.print(f'Персонал: {len(self.__staff)} из 3')

    def is_ready(self) -> bool:
        if len(self.__staff) < 3:
            self.__cli_print.print(f'Недостаточно персонала: {len(self.__staff)} из 3')
            return False
        return True

    def check_service_quality(self, booking_data: BookingDict) -> bool:
        self.__cli_print.print("=== ПРИЯТНОГО ВРЕМЯПРЕПРОВОЖДЕНИЯ! ===")
        time.sleep(2)

        if booking_data['room_quality'] < self.__required_service_level:
            self.__cli_print.print('Номер не соответствует ожиданиям гостя!')
            return False
        if booking_data['service_level'] < self.__required_service_level:
            self.__cli_print.print('Уровень сервиса недостаточен!')
            return False
        self.__cli_print.print('Обслуживание подтверждено! Гость доволен!')
        return True