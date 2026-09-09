from pydantic import BaseModel, Field, ValidationError, field_validator
import re
from cli_input import CliInput
from cli_print import CliPrint


class Schema(BaseModel):
    name: str = Field(...)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Поле не может быть пустым!")
        if len(value) < 2:
            raise ValueError("Введите больше 2 символов!")
        if len(value) > 30:
            raise ValueError("Введите меньше 30 символов!")
        if not re.match(r'^[А-ЯЁа-яё][а-яё]*(-[А-ЯЁа-яё][а-яё]*)?$', value):
            raise ValueError(
                "Неверный ввод! Введите корректно!"
            )
        return value


class Person:
    __cli_input = CliInput()
    _first_name: str = ''
    _last_name: str = ''
    _surname: str = ''
    __cli_print: CliPrint = CliPrint()

    def _get_valid_input(self, field_name: str) -> str:
        while True:
            self.__cli_input.set_input(f"Введите {field_name}: ")
            value = self.__cli_input.get_input().strip()
            try:
                validated_data = Schema(name=value)
                return validated_data.name
            except ValidationError as e:
                err = e.errors()[0]["msg"].split(', ')[1]
                self.__cli_print.print(err)

    def add_person(self):
        self._last_name = self._get_valid_input("Фамилия")
        self._first_name = self._get_valid_input("Имя")
        self._surname = self._get_valid_input("Отчество")