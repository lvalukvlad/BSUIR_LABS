from sorce.book import Book


class CreatedBooks:
    __title: str | None = None
    __author_first_name: str | None = None
    __author_last_name: str | None = None
    __publisher: str | None = None
    __volumes: str | None = None
    __copies: str | None = None

    def get_book(self) -> Book | None:
        if not self.__title:
            return None
        if not self.__author_first_name:
            return None
        if not self.__author_last_name:
            return None
        if not self.__publisher:
            return None
        if not self.__volumes:
            return None
        if not self.__copies:
            return None
        return {
            'title': self.__title,
            'author': self.__author_first_name + ' ' + self.__author_last_name,
            'publisher': self.__publisher,
            'volumes': self.__volumes,
            'copies': self.__copies,
            'total_volumes': str(int(self.__volumes) * int(self.__copies))
        }

    def set_title(self, title: str):
        if title:
            self.__title = title.strip()
        else:
            self.__title = None

    def get_title(self) -> str | None:
        return self.__title

    def set_author_first_name(self, author_first_name: str):
        if author_first_name:
            self.__author_first_name = author_first_name.strip()
        else:
            self.__author_first_name = None

    def get_author_first_name(self) -> str | None:
        return self.__author_first_name

    def set_author_last_name(self, author_last_name: str):
        if author_last_name:
            self.__author_last_name = author_last_name.strip()
        else:
            self.__author_last_name = None

    def get_author_last_name(self) -> str | None:
        return self.__author_last_name

    def set_publisher(self, publisher: str):
        if publisher:
            self.__publisher = publisher.strip()
        else:
            self.__publisher = None

    def get_publisher(self) -> str | None:
        return self.__publisher

    def set_volumes(self, volumes: str):
        if volumes:
            self.__volumes = volumes.strip()
        else:
            self.__volumes = None

    def get_volumes(self) -> str | None:
        return self.__volumes

    def set_copies(self, copies: str):
        if copies:
            self.__copies = copies.strip()
        else:
            self.__copies = None

    def get_copies(self) -> str | None:
        return self.__copies