import flet as ft
from typing import List
from sorce.book import Book
from sorce.get_books import get_books
from components.list_of_books import list_of_books
from sorce.highlighted_books import HighlightedBooks
from components.pagination import pagination
from sorce.book_page import BookPage
from sorce.create_book import create_book
from components.create_input_form import create_input_form
from sorce.created_book import CreatedBooks
from sorce.delete_books import delete_books
from sorce.validate_create_book import validate_create_book
from components.error_file_element import error_file_element


def create_menu(page: ft.Page, file_path: str, close_dialog):
    if file_path == '':
        close_dialog()
        return error_file_element(close_dialog)

    books: List[Book] = get_books(file_path)
    book_page: BookPage = BookPage()
    highlighted_books: HighlightedBooks = HighlightedBooks(books)
    created_book: CreatedBooks = CreatedBooks()
    error_value: str = ''
    error = ft.Column(
                controls=[
                    ft.Text(value=f"{error_value}", size=14, color='#E54D2E')
                ],
                alignment=ft.alignment.center_right
            )

    def update_error():
        nonlocal error
        error.controls.clear()
        error.controls.append(
            ft.Text(value=f"{error_value}", size=14, color='#E54D2E')
        )
        page.update()

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
        nonlocal error_value
        error_value = ''
        books_container.controls.clear()
        update_list_of_book()
        books_container.controls.append(out_books)
        if highlighted_books.get_books():
            books_container.controls.append(
                pagination(page, len(highlighted_books.get_books()), book_page, update_list_of_book))
        if not error_value:
            error_value = ''
            update_error()
        page.update()

    result_input_form = ft.Column(
        controls=[create_input_form(highlighted_books, created_book, update_highlighted_books)]
    )

    def update_input_form():
        result_input_form.controls.clear()
        result_input_form.controls.append(
            create_input_form(highlighted_books, created_book, update_highlighted_books)
        )

    def create_book_parameters_to_none():
        nonlocal created_book
        created_book.set_title('')
        created_book.set_publisher('')
        created_book.set_copies('')
        created_book.set_volumes('')
        created_book.set_author_first_name('')
        created_book.set_author_last_name('')
        created_book.set_title('')

    def highlighted_books_parameters_to_none():
        highlighted_books.set_title('')
        highlighted_books.set_publisher('')
        highlighted_books.set_max_total_volumes('')
        highlighted_books.set_max_copies('')
        highlighted_books.set_max_volumes('')
        highlighted_books.set_min_copies('')
        highlighted_books.set_min_volumes('')
        highlighted_books.set_min_total_volumes('')
        highlighted_books.set_author_first_name('')
        highlighted_books.set_author_last_name('')
        highlighted_books.set_title('')
        create_book_parameters_to_none()
        update_input_form()

    def create_highlighted_books():
        nonlocal books, highlighted_books, created_book, error_value
        if created_book.get_book():
            error_value = validate_create_book(created_book)
            if error_value:
                update_error()
                return
            for book in books:
                if (
                    created_book.get_author_first_name() in book['author'] and
                    created_book.get_author_last_name() in book['author'] and
                    created_book.get_publisher() in book['publisher'] and
                    created_book.get_title() in book['title']
                ):
                    delete_books(file_path, [created_book.get_book()])
            create_book(file_path, created_book.get_book())
            books = get_books(file_path)
            highlighted_books.books = books
            highlighted_books_parameters_to_none()
            update_highlighted_books()
            close_dialog()
            return
        error_value = 'Не заполнены все поля'
        update_error()
        return

    return ft.Container(
                content=ft.Column(
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
                                ft.Text('Создание книг', size=24, color='#FDD3E8'),
                                ft.Container(
                                    expand=1,
                                    content=ft.ElevatedButton(
                                        'Создание', height=38, width=120, bgcolor='#46A758', color='#FDD3E8',
                                        on_click=lambda _: create_highlighted_books()
                                    ),
                                    alignment=ft.alignment.center_right
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        error,
                        result_input_form,
                        books_container
                    ],
                    width=page.width,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                )
            )