import time

import cli_input
from student import Student
from commission import Commission
from scientific_director import ScientificDirector
from transitions import Machine
from cli_input import CliInput
from cli_print import CliPrint


class Menu:
    __cli_print: CliPrint = CliPrint()
    __cli_input: CliInput = CliInput()
    state: str
    __student = Student()
    __scientific_director = ScientificDirector()
    __commission = Commission()
    __menu_items = {
        'creation': [
            '1 - Добавить студента',
            '2 - Добавить научного руководителя',
            '3 - Создать презентацию',
            '4 - Создать доклад',
            '5 - Перейти к следующему этапу',
            '0 - Выход из программы'],
        'preparation': [
            '1 - Рецензирование работы',
            '2 - Скорректировать презентацию',
            '3 - Скорректировать доклад',
            '4 - Добавить члена комиссии',
            '5 - Перейти к следующему этапу',
            '0 - Выход из программы'],
        'rehearsal': [
            '1 - Репетиция защиты',
            '2 - Скорректировать презентацию',
            '3 - Скорректировать доклад',
            '4 - Перейти к последнему этапу',
            '0 - Выход из программы'],
        'submission_of_thesis': [
            'Вопрос:'
        ]
    }
    states = ['creation', 'preparation', 'rehearsal', 'submission_of_thesis']

    def __init__(self):
        self.machine = Machine(model=self, states=Menu.states, initial="creation")
        self.machine.add_transition("go_to_preparation", "creation", "preparation")
        self.machine.add_transition("go_to_rehearsal", "preparation", "rehearsal")
        self.machine.add_transition("go_to_submission_of_thesis", "rehearsal", "submission_of_thesis")

    def creation_menu(self):
        while True:
            for element in self.__menu_items[self.state]:
                self.__cli_print.print(element)
            choice: int
            self.__cli_input.set_input('Ввод: ')
            input_str: str = self.__cli_input.get_input()
            try:
                choice: int = int(input_str)
            except ValueError:
                self.__cli_print.print("Ошибка: введите целое число.")
                continue
            if '1 - Добавить студента' in self.__menu_items['creation'] and choice == 1:
                self.__student.add_student()
                self.__menu_items['creation'].remove('1 - Добавить студента')
            elif '2 - Добавить научного руководителя' in self.__menu_items['creation'] and choice == 2:
                self.__scientific_director.add_scientific_director()
                self.__menu_items['creation'].remove('2 - Добавить научного руководителя')
            elif choice == 3:
                self.__student.create_presentation()
            elif choice == 4:
                self.__student.create_report()
            elif choice == 5:
                if self.__student.get_diploma_project()['presentation'] != 0 and \
                    self.__student.get_diploma_project()['report'] != 0 and \
                        self.__scientific_director.is_exist() and \
                        self.__student.is_exist():
                    self.go_to_preparation()
                    self.menu()
                    break
                else:
                    self.__cli_print.print('Не выполнены все действия')
            elif choice == 0:
                return
            else:
                continue

    def preparation_menu(self):
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
                self.__cli_print.print("Ошибка: введите целое число.")
                continue
            if choice == 1:
                verification = self.__scientific_director.verification_of_the_graduation_project(
                    self.__student.get_diploma_project()
                )
            elif choice == 2:
                self.__student.presentation_revision()
            elif choice == 3:
                self.__student.report_revision()
            elif choice == 4:
                self.__commission.add_committeeman()
            elif choice == 5:
                if verification and self.__commission.commission_is():
                    self.go_to_rehearsal()
                    self.menu()
                    break
                self.__cli_print.print('Не выполнены все действия')
            elif choice == 0:
                return
            else:
                continue

    def rehearsal_menu(self):
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
                self.__cli_print.print("Ошибка: введите целое число.")
                continue
            if choice == 1:
                verification = self.__commission.rehearsal_diploma_project(
                    self.__student.get_diploma_project()
                )
            elif choice == 2:
                self.__student.presentation_revision()
            elif choice == 3:
                self.__student.report_revision()
            elif choice == 4:
                if verification:
                    self.go_to_submission_of_thesis()
                    self.menu()
                    break
                self.__cli_print.print('Не выполнены все действия')
            elif choice == 0:
                return
            else:
                continue

    def submission_of_thesis_menu(self):
        verification: bool = False
        while True:
            self.__student.set_mark(5)
            self.__cli_print.print('Вам повезло, вопросы сегодня простые')
            self.__cli_input.set_input('Напишите Имя вашего научного руководителя:')
            scientific_director_first_name: str = self.__cli_input.get_input().strip()
            if scientific_director_first_name == self.__scientific_director.get_first_name():
                self.__student.set_mark(self.__student.get_mark() + 1)
            else:
                self.__cli_print.print('Вы даже не знаете как зовут вашего научного руководителя')
            self.__cli_input.set_input('Напишите Отчество вашего научного руководителя:')
            scientific_director_surname: str = self.__cli_input.get_input().strip()
            if scientific_director_surname == self.__scientific_director.get_surname():
                self.__student.set_mark(self.__student.get_mark() + 1)
            else:
                self.__cli_print.print('Вы даже не знаете отчества вашего научного руководителя')
            self.__cli_input.set_input('Будете ли вы дальше работать по специальности?\n'
                                       '1 - Да\n'
                                       '2 - Нет\n'
                                       'Ввод: '
                                       )
            future_work: str = self.__cli_input.get_input().strip()
            self.__student.set_mark(self.__student.get_mark() + 1) if future_work == '1' else self.__cli_print.print(
                'Жаль'
            )
            self.__cli_input.set_input('Пользовались ли вы нейронными сетями при выполнении работы?\n'
                                       '1 - Да \n'
                                       '2 - Нет\n'
                                       'Ввод: '
                                       )
            neural_network: str = self.__cli_input.get_input().strip()
            self.__student.set_mark(self.__student.get_mark() + 1) if neural_network == '1' else self.__cli_print.print(
                'Сомневаюсь'
            )
            self.__cli_print.print('Мы посовещаемся и решим')
            time.sleep(2)
            if self.__commission.get_max_difficulty() < 95:
                self.__student.set_mark(self.__student.get_mark() + 1)
                self.__cli_print.print('Ваша дипломная работа достойна пахлавы(дает пахлаву)')
            time.sleep(0.5)
            self.__cli_print.print(
                f'Ваша итоговая оценка {self.__student.get_mark()}, поздравляем!(хлопки из-за двери)'
            )
            break

    def menu(self):
        menu_functions = {
            'creation': self.creation_menu,
            'preparation': self.preparation_menu,
            'rehearsal': self.rehearsal_menu,
            'submission_of_thesis': self.submission_of_thesis_menu
        }
        current_menu = menu_functions[self.state]
        current_menu()