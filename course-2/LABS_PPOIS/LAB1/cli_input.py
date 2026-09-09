class CliInput:
    __text: str

    def set_input(self, output):
        self.__text = input(output)

    def get_input(self) -> str:
        return self.__text
