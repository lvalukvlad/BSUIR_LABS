import xml.sax
import xml.sax.saxutils
import os
from sorce.book import Book
from typing import List


class BookHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.books = []
        self.current_data = ""
        self.current_book = {}

    def startElement(self, tag, attributes):
        self.current_data = tag
        if tag == "book":
            self.current_book = {}

    def characters(self, content):
        if self.current_data and content.strip():
            self.current_book[self.current_data] = content.strip()

    def endElement(self, tag):
        if tag == "book" and self.current_book:
            self.books.append(self.current_book)
        self.current_data = ""

def delete_books(file_path: str, list_of_books: List[Book]):
    try:
        if not os.path.exists(file_path):
            print(f"Ошибка: файл '{file_path}' не найден.")
            return

        handler = BookHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(file_path)

        deleted = False
        updated_books = []

        for book in handler.books:
            if not any(
                book.get("title") == deleted_book["title"] and
                book.get("author") == deleted_book["author"] and
                book.get("publisher") == deleted_book["publisher"]
                for deleted_book in list_of_books
            ):
                updated_books.append(book)
            else:
                deleted = True

        if deleted:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write("<books>\n")
                for b in updated_books:
                    f.write("  <book>\n")
                    for key, value in b.items():
                        tag = xml.sax.saxutils.escape(key)
                        text = xml.sax.saxutils.escape(value)
                        f.write(f"    <{tag}>{text}</{tag}>\n")
                    f.write("  </book>\n")
                f.write("</books>\n")
            print("Файл успешно обновлен!")
        else:
            print("Книги для удаления не найдены.")
    except xml.sax.SAXParseException:
        print(f"Ошибка: некорректный XML-файл '{file_path}'.")