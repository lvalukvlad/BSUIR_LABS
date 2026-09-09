from typing import List
from sorce.book import Book


class HighlightedBooks:
    __books: List[Book]
    __title: str | None = None
    __author_first_name: str | None = None
    __author_last_name: str | None = None
    __publisher: str | None = None
    __min_volumes: str | None = None
    __max_volumes: str | None = None
    __min_copies: str | None = None
    __max_copies: str | None = None
    __min_total_volumes: str | None = None
    __max_total_volumes: str | None = None

    def __init__(self, books: List[Book] | None):
        self.__books = books

    @property
    def books(self):
        return self.__books

    @books.setter
    def books(self, books):
        self.__books = books

    def get_books(self) -> List[Book] | None:
        highlighted_books: List[Book] | List = []
        for book in self.__books:
            if self.__title and self.__title not in book['title']:
                continue
            if self.__author_first_name and self.__author_first_name not in book['author'].split(' ', 1)[0]:
                continue
            if self.__author_last_name and self.__author_last_name not in book['author'].split(' ', 1)[1]:
                continue
            if self.__publisher and self.__publisher not in book['publisher']:
                continue
            if self.__min_volumes and int(book['volumes']) < int(self.__min_volumes):
                continue
            if self.__max_volumes and int(book['volumes']) > int(self.__max_volumes):
                continue
            if self.__min_copies and int(book['copies']) < int(self.__min_copies):
                continue
            if self.__max_copies and int(book['copies']) > int(self.__max_copies):
                continue
            if self.__min_total_volumes and int(book['total_volumes']) < int(self.__min_total_volumes):
                continue
            if self.__max_total_volumes and int(book['total_volumes']) > int(self.__max_total_volumes):
                continue
            highlighted_books.append(book)
        if len(highlighted_books) < 1:
            return None
        return highlighted_books

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

    def set_min_volumes(self, min_volumes: str):
        if min_volumes:
            self.__min_volumes = min_volumes.strip()
        else:
            self.__min_volumes = None

    def get_min_volumes(self) -> str | None:
        return self.__min_volumes

    def set_max_volumes(self, max_volumes: str):
        if max_volumes:
            self.__max_volumes = max_volumes.strip()
        else:
            self.__max_volumes = None

    def get_max_volumes(self) -> str | None:
        return self.__max_volumes

    def set_min_copies(self, min_copies: str):
        if min_copies:
            self.__min_copies = min_copies.strip()
        else:
            self.__min_copies = None

    def get_min_copies(self) -> str | None:
        return self.__min_copies

    def set_max_copies(self, max_copies: str):
        if max_copies:
            self.__max_copies = max_copies.strip()
        else:
            self.__max_copies = None

    def get_max_copies(self) -> str | None:
        return self.__max_copies

    def set_min_total_volumes(self, min_total_volumes: str):
        if min_total_volumes:
            self.__min_total_volumes = min_total_volumes.strip()
        else:
            self.__min_total_volumes = None

    def get_min_total_volumes(self) -> str | None:
        return self.__min_total_volumes

    def set_max_total_volumes(self, max_total_volumes: str):
        if max_total_volumes:
            self.__max_total_volumes = max_total_volumes.strip()
        else:
            self.__max_total_volumes = None

    def get_max_total_volumes(self) -> str | None:
        return self.__max_total_volumes