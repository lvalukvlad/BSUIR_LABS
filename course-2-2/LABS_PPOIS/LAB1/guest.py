import time
from typing import TypedDict
from booking import Booking
from person import Person
from cli_print import CliPrint


class BookingDict(TypedDict):
    room_quality: int
    service_level: int


class Guest(Person):
    def __init__(self):
        super().__init__()
        self.__booking = Booking()
        self.__services = {'cleaning': False, 'food': False}
        self.__cli_print: CliPrint = CliPrint()

    def add_guest(self):
        self.add_person()
        self.__cli_print.print(f"Гость {self._last_name} {self._first_name} {self._surname} зарегистрирован!")

    def is_exist(self) -> bool:
        return bool(self._surname)

    def select_room(self):
        art = r"""
       ___________
      |           |
      |    🛏️     |  
      |___________|
        """
        self.__cli_print.print(art)
        time.sleep(1)
        self.__booking.select_room()

    def upgrade_room(self):
        self.__booking.upgrade_room()

    def select_services(self):
        art = r"""
       ___________
      |  🍽️  🧼   |
      |   Услуги  |
      |___________|
        """
        self.__cli_print.print(art)
        time.sleep(1)
        self.__booking.select_service()

    def upgrade_services(self):
        self.__booking.upgrade_service()

    def order_cleaning(self):
        self.__services['cleaning'] = True
        self.__cli_print.print("Уборка номера заказана (+$15) 🧹")

    def order_food(self):
        self.__services['food'] = True
        self.__cli_print.print("Питание заказано (+$25) 🍕")

    def get_services_cost(self) -> int:
        return 15 * self.__services['cleaning'] + 25 * self.__services['food']

    def get_booking_data(self) -> BookingDict:
        return self.__booking.get_booking_data()

    def set_price(self, price: int):
        self.__booking.set_price(price)

    def get_price(self) -> int:
        return self.__booking.get_price()
