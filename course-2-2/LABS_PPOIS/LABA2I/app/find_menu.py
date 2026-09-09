import flet as ft
from typing import List
from sorce.book import Book
from sorce.get_books import get_books
from components.list_of_books import list_of_books
from sorce.highlighted_books import HighlightedBooks
from components.pagination import pagination
from sorce.book_page import BookPage
from components.input_form import input_form
from components.error_file_element import error_file_element


def find_menu(page: ft.Page, file_path: str, close_dialog):
    if file_path == '':
        close_dialog()
        return error_file_element(close_dialog)
    books: List[Book] = get_books(file_path)
    book_page: BookPage = BookPage()
    highlighted_books: HighlightedBooks = HighlightedBooks(books)
    out_books = ft.Column(
        controls=[
            list_of_books(page, highlighted_books.get_books(), book_page)
        ]
    )

    def update_list_of_book():
        out_books.controls.clear()
        out_books.controls.append(list_of_books(page, highlighted_books.get_books(), book_page))
        page.update()
    if highlighted_books.get_books():
        books_container = ft.Column(
            controls=[
                out_books,
                pagination(page, len(highlighted_books.get_books()), book_page, update_list_of_book)
            ]
        )
    else:
        books_container = ft.Column(
            controls=[
                out_books,
            ]
        )

    def update_highlighted_books():
        books_container.controls.clear()
        update_list_of_book()
        books_container.controls.append(out_books)
        if highlighted_books.get_books():
            books_container.controls.append(
                pagination(page, len(highlighted_books.get_books()), book_page, update_list_of_book))
        page.update()

    result_input_form = ft.Column(
        controls=[input_form(page, highlighted_books, update_highlighted_books)]
    )

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        expand=1,
                        content=ft.ElevatedButton(
                            "Закрыть", color="#FDD3E8", on_click=close_dialog, height=38, width=120,
                        ),
                        alignment=ft.alignment.center_left
                    ),
                    ft.Text('Поиск книг', size=24, color='#FDD3E8'),
                    ft.Container(expand=1)
                ],
            ),
            result_input_form,
            books_container
        ],
        width=page.width,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True
    )