import random
from typing import TypedDict
from cli_print import CliPrint


class DiplomaProjectDict(TypedDict):
    presentation: int
    report: int


class DiplomaProject:
    __presentation: int = 0
    __report: int = 0
    __mark: int = 0
    __cli_print: CliPrint = CliPrint()

    def presentation_create(self):
        self.__presentation = 20 + random.randrange(1, 80, 1)
        self.__cli_print.print(f'Полнота раскрытия темы {self.__presentation}%')

    def report_create(self):
        self.__report = 20 + random.randrange(1, 80, 1)
        self.__cli_print.print(f'Полнота раскрытия темы {self.__report}%')

    def presentation_revision(self):
        self.__presentation = self.__presentation + random.randrange(1, 30, 1)
        if self.__presentation > 100:
            self.__presentation = 100
        self.__cli_print.print(f'Теперь полнота раскрытия темы {self.__presentation}%')

    def report_revision(self):
        self.__report = self.__report + random.randrange(1, 30, 1)
        if self.__report > 100:
            self.__report = 100
        self.__cli_print.print(f'Теперь полнота раскрытия темы {self.__report}%')

    def get_diploma_project(self) -> DiplomaProjectDict:
        return {'presentation': self.__presentation, 'report': self.__report}

    def set_mark(self, mark: int):
        self.__mark = mark

    def get_mark(self) -> int:
        return self.__mark