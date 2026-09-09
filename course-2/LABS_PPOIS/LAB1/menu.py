import time
from cli_input import CliInput
from cli_print import CliPrint
from guest import Guest
from reception import Reception
from staff import Staff
from transitions import Machine


class Menu:
    __cli_print: CliPrint = CliPrint()
    __cli_input: CliInput = CliInput()
    state: str
    __guest = Guest()
    __receptionist = Staff()
    __reception = Reception()
    __menu_items = {
        'booking': [
            '1 - Зарегистрировать гостя',
            '2 - Добавить администратора',
            '3 - Выбрать номер',
            '4 - Выбрать услуги',
            '5 - Перейти к заселению',
            '0 - Выход'
        ],
        'check_in': [
            '1 - Подтвердить бронь',
            '2 - Улучшить номер',
            '3 - Добавить услуги',
            '4 - Добавить сотрудника',
            '5 - Перейти к сервисам',
            '0 - Выход'
        ],
        'services': [
            '1 - Проверить качество обслуживания',
            '2 - Заказать уборку',
            '3 - Заказать питание',
            '4 - Перейти к выселению',
            '0 - Выход'
        ],
        'check_out': [
            'Оплата и отзыв:'
        ]
    }
    states = ['booking', 'check_in', 'services', 'check_out']

    def __init__(self):
        self.machine = Machine(model=self, states=Menu.states, initial="booking")
        self.machine.add_transition("go_to_check_in", "booking", "check_in")
        self.machine.add_transition("go_to_services", "check_in", "services")
        self.machine.add_transition("go_to_check_out", "services", "check_out")

    def booking_menu(self):
        while True:
            for element in self.__menu_items[self.state]:
                self.__cli_print.print(element)
            choice: int
            self.__cli_input.set_input('Ввод: ')
            input_str: str = self.__cli_input.get_input()
            try:
                choice: int = int(input_str)
            except ValueError:
                self.__cli_print.print("Ошибка: введите число.")
                continue

            if choice == 1:
                self.__guest.add_guest()
                self.__menu_items['booking'].remove('1 - Зарегистрировать гостя')
            elif choice == 2:
                self.__receptionist.add_staff()
                self.__menu_items['booking'].remove('2 - Добавить администратора')
            elif choice == 3:
                self.__guest.select_room()
            elif choice == 4:
                self.__guest.select_services()
            elif choice == 5:
                if (self.__guest.get_booking_data()['room_quality'] != 0
                        and self.__guest.get_booking_data()['service_level'] != 0
                        and self.__receptionist.is_exist()
                        and self.__guest.is_exist()):
                    self.go_to_check_in()
                    self.menu()
                    break
                else:
                    self.__cli_print.print('Не все данные заполнены!')
            elif choice == 0:
                return
            else:
                continue

    def check_in_menu(self):
        verification: bool = False
        while True:
            for element in self.__menu_items[self.state]:
                self.__cli_print.print(element)
            choice: int
            self.__cli_input.set_input('Ввод: ')
            input_str: str = self.__cli_input.get_input()
            try:
                choice: int = int(input_str)
            except ValueError:
                self.__cli_print.print("Ошибка: введите число.")
                continue

            if choice == 1:
                verification = self.__receptionist.confirm_booking(
                    self.__guest.get_booking_data()
                )
            elif choice == 2:
                self.__guest.upgrade_room()
            elif choice == 3:
                self.__guest.upgrade_services()
            elif choice == 4:
                self.__reception.add_staff()
            elif choice == 5:
                if verification and self.__reception.is_ready():
                    self.go_to_services()
                    self.menu()
                    break
                elif not verification:
                    self.__cli_print.print('Бронирование не подтверждено!')
                else:
                    self.__cli_print.print('Недостаточно персонала!')
            elif choice == 0:
                return
            else:
                continue

    def services_menu(self):
        verification: bool = False
        while True:
            for element in self.__menu_items[self.state]:
                self.__cli_print.print(element)
            choice: int
            self.__cli_input.set_input('Ввод: ')
            input_str: str = self.__cli_input.get_input()
            try:
                choice: int = int(input_str)
            except ValueError:
                self.__cli_print.print("Ошибка: введите число.")
                continue

            if choice == 1:
                verification = self.__reception.check_service_quality(
                    self.__guest.get_booking_data()
                )
            elif choice == 2:
                self.__guest.order_cleaning()
            elif choice == 3:
                self.__guest.order_food()
            elif choice == 4:
                self.go_to_check_out()
                self.menu()
                break
            elif choice == 0:
                return
            else:
                continue

    def check_out_menu(self):
        base_price = 100
        services_cost = self.__guest.get_services_cost()
        total = base_price + services_cost

        self.__cli_print.print('\n=== Расчет стоимости ===')
        self.__cli_print.print(f'{"Базовая цена":<20} ${base_price}')
        if services_cost > 0:
            self.__cli_print.print(f'{"Доп. услуги":<20} +${services_cost}')

        self.__cli_input.set_input('\nНазовите имя администратора (скидка $5): ')
        if self.__cli_input.get_input().strip().lower() == self.__receptionist.get_first_name().lower():
            total -= 5
            self.__cli_print.print(f'{"Скидка за имя":<20} -$5')

        while True:
            self.__cli_input.set_input('\nОцените номер (1-5★). 5★ = скидка $10: ')
            rating = self.__cli_input.get_input().strip()
            if rating.isdigit() and 1 <= int(rating) <= 5:
                discount = int(rating) * 2
                total -= discount
                self.__cli_print.print(f'{"Скидка за " + rating + "★":<20} -${discount}')
                break
            self.__cli_print.print('Ошибка: введите число от 1 до 5')

        while True:
            self.__cli_input.set_input('\nОцените чистоту (1-5). 5★ = скидка $10: ')
            rating = self.__cli_input.get_input().strip()
            if rating.isdigit() and 1 <= int(rating) <= 5:
                discount = int(rating) * 2
                total -= discount
                self.__cli_print.print(f'{"Скидка за чистоту":<20} -${discount}')
                break
            self.__cli_print.print('Ошибка: введите число от 1 до 5')

        while True:
            self.__cli_input.set_input('\nОцените обслуживание (1-5). 5★ = скидка $15: ')
            rating = self.__cli_input.get_input().strip()
            if rating.isdigit() and 1 <= int(rating) <= 5:
                discount = int(rating) * 3
                total -= discount
                self.__cli_print.print(f'{"Скидка за обслуживание":<20} -${discount}')
                break
            self.__cli_print.print('Ошибка: введите число от 1 до 5')

        while True:
            self.__cli_input.set_input('\nПорекомендуете отель? (1-да/+$10, 0-нет/+$0): ')
            answer = self.__cli_input.get_input().strip()
            if answer in ('0', '1'):
                if answer == '1':
                    total -= 10
                    self.__cli_print.print(f'{"Скидка за рекомендацию":<20} -$10')
                break
            self.__cli_print.print('Ошибка: введите 0 или 1')

        total = max(total, 60)

        self.__cli_print.print('\n' + '=' * 40)
        self.__cli_print.print(f'{"ИТОГО":<20} ${total}')
        self.__cli_print.print('=' * 40 + '\n')
        self.__cli_print.print('Спасибо за посещение! Ждем вас снова! 🏨')
        exit()

    def menu(self):
        menu_functions = {
            'booking': self.booking_menu,
            'check_in': self.check_in_menu,
            'services': self.services_menu,
            'check_out': self.check_out_menu
        }
        current_menu = menu_functions[self.state]
        current_menu()
