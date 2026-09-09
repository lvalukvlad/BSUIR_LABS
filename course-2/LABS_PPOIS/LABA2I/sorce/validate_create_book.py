import re
from sorce.created_book import CreatedBooks

def validate_create_book(created_book: CreatedBooks) -> str:
    if not re.match(r"^[А-ЯЁ][а-яё]+(?:[-' ]?[А-ЯЁ][а-яё]+)*$", created_book.get_author_first_name()):
        return 'Неверно записано имя автора'

    if not re.match(r"^[А-ЯЁ][а-яё]+(?:[-' ]?[А-ЯЁ][а-яё]+)*$", created_book.get_author_last_name()):
        return 'Неверно записана фамилия автора'

    if not re.match(r"^[A-Za-zА-ЯЁа-яё0-9\s\-'\".,!?;:]+$", created_book.get_publisher()):
        return 'Неверно записано издательство'