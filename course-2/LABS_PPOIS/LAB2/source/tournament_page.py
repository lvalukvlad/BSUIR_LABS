class TournamentPage:
    __current_page: int = 1
    __items_per_page: int = 10

    def set_current_page(self, current_page: int):
        self.__current_page = current_page

    def set_items_per_page(self, items_per_page: int):
        self.__items_per_page = items_per_page

    def get_current_page(self) -> int:
        return self.__current_page

    def get_items_per_page(self) -> int:
        return self.__items_per_page