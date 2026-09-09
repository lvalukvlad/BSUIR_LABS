import time
from committeeman import Committeeman
from typing import TypedDict, List
from cli_print import CliPrint


class DiplomaProjectDict(TypedDict):
    presentation: int
    report: int


class Commission:
    __commission: List[Committeeman] = []
    __max_difficulty: int = 0
    __upcoming_before_max_difficulty: int = 0
    __cli_print: CliPrint = CliPrint()

    def add_committeeman(self):
        committeeman = Committeeman()
        committeeman.add_committeeman()
        self.__commission.append(committeeman)
        self.__cli_print.print(f'Комиссия заполнена на {len(self.__commission)} из 3')
        if committeeman.get_difficulty() > self.__upcoming_before_max_difficulty:
            self.__upcoming_before_max_difficulty = committeeman.get_difficulty()
            if self.__upcoming_before_max_difficulty > self.__max_difficulty:
                self.__upcoming_before_max_difficulty = self.__upcoming_before_max_difficulty - self.__max_difficulty
                self.__max_difficulty = self.__max_difficulty + self.__upcoming_before_max_difficulty
                self.__upcoming_before_max_difficulty = self.__max_difficulty - self.__upcoming_before_max_difficulty
        return

    def commission_is(self) -> bool:
        if len(self.__commission) < 3:
            self.__cli_print.print(f'Комиссия не набрана {len(self.__commission)} из 3')
            return False
        return True

    def rehearsal_diploma_project(self, diploma_project_dict: DiplomaProjectDict) -> bool:
        self.__cli_print.print(r"""
          |____________________________________________________|
          | __     __   ____   ___ ||  ____    ____     _  __  |
          ||  |__ |--|_| || |_|   |||_|**|*|__|+|+||___| ||  | |
          ||==|^^||--| |=||=| |=*=||| |~~|~|  |=|=|| | |~||==| |
          ||  |##||  | | || | |Gal|||-|Ov| |==|+|+||-|-|~||__| |
          ||__|__||__|_|_||_|_|___|||_|__|_|__|_|_||_|_|_||__|_|
          ||_______________________||__________________________|
          | _____________________  ||      __   __  _  __    _ |
          ||=|=|=|=|=|=|=|=|=|=|=| __..\/ |  |_|  ||#||==|  / /|
          || | | | | | | | | | | |/\ \  \\|++|=|  || ||==| / / |
          ||_|_|_|_|_|_|_|_|_|_|_/_/\_.___\__|_|__||_||__|/_/__|
          |____________________ /\~()/()~//\ __________________|
          | __   __    _  _     \_  (_ .  _/ _    ___     _____|
          ||~~|_|..|__| || |_ _   \ //\\ /  |=|__|~|~|___| | | |
          ||--|+|^^|==|1||2| | |__/\ __ /\__| |==|x|x|+|+|=|=|=|
          ||__|_|__|__|_||_|_| /  \ \  / /  \_|__|_|_|_|_|_|_|_|
          |_________________ _/    \/\/\/    \_ _______________|
          | _____   _   __  |/      \../      \|  __   __   ___|
          ||_____|_| |_|##|_||   |   \/ __|   ||_|==|_|++|_|-|||
          ||______||=|#|--| |\   \   o    /   /| |  |~|  | | |||
          ||______||_|_|__|_|_\   \  o   /   /_|_|__|_|__|_|_|||
          |_________ __________\___\____/___/___________ ______|
          |__    _  /    ________     ______           /| _ _ _|
          |\ \  |=|/   //    /| //   /  /  / |        / ||%|%|%|
          | \/\ |*/  .//____//.//   /__/__/ (_)      /  ||=|=|=|
        __|  \/\|/   /(____|/ //                    /  /||~|~|~|__
          |___\_/   /________//   ________         /  / ||_|_|_|
          |___ /   (|________/   |\_______\       /  /| |______|
              /                  \|________)     /  / | |
                """)
        time.sleep(2)
        if diploma_project_dict['presentation'] < self.__upcoming_before_max_difficulty:
            self.__cli_print.print('Презентация не смогла в достаточной мере раскрыть тему')
            return False
        if diploma_project_dict['report'] < self.__max_difficulty:
            self.__cli_print.print('Доклад не смог в достаточной мере раскрыть тему')
            return False
        self.__cli_print.print('Всё хорошо, можем приступить к сдаче дипломного проекта!')
        return True

    def get_max_difficulty(self) -> int:
        return self.__max_difficulty