import xml.sax
import xml.sax.saxutils
import os
from sorce.book import Book


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


def create_book(file_path: str, book: Book):
    try:
        handler = BookHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)

        if os.path.exists(file_path):
            parser.parse(file_path)

        handler.books = [b for b in handler.books if b]

        handler.books.insert(0, book)

        print("Проверка данных перед записью:", handler.books)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write("<books>\n")
            for b in handler.books:
                if not b:
                    continue
                f.write("  <book>\n")
                for key, value in b.items():
                    tag = xml.sax.saxutils.escape(key.replace('_v', 'V'))
                    text = xml.sax.saxutils.escape(value)
                    f.write(f"    <{tag}>{text}</{tag}>\n")
                f.write("  </book>\n")
            f.write("</books>\n")
    except Exception as e:
        print(f"Ошибка: {e}")