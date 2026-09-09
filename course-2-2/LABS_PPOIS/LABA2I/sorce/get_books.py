import xml.dom.minidom as minidom
from sorce.book import Book
from typing import List


def get_books(file_path: str) -> List[Book]:
    books: List[Book] | List = []
    try:
        dom = minidom.parse(file_path)
        root = dom.documentElement

        book_nodes = root.getElementsByTagName('book')
        for book in book_nodes:
            def get_text(tag_name: str) -> str:
                element = book.getElementsByTagName(tag_name)
                return element[0].firstChild.nodeValue if element and element[0].firstChild else ''

            book_data = {
                'title': get_text('title'),
                'author': get_text('author'),
                'publisher': get_text('publisher'),
                'volumes': get_text('volumes'),
                'copies': get_text('copies'),
                'total_volumes': get_text('totalVolumes')
            }
            books.append(book_data)
    except FileNotFoundError:
        print(f"Ошибка: файл '{file_path}' не найден.")
    except Exception as e:
        print(f"Произошла ошибка при разборе XML: {e}")

    return books