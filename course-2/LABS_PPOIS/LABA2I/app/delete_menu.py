import flet as ft
from typing import List
from sorce.book import Book
from sorce.get_books import get_books
from components.list_of_books import list_of_books
from sorce.highlighted_books import HighlightedBooks
from components.pagination import pagination
from sorce.book_page import BookPage
from sorce.delete_books import delete_books
from components.input_form import input_form
from components.error_file_element import error_file_element
from components.delete_dialog_element import delete_dialog_element


def delete_menu(page: ft.Page, file_path: str, close_dialog):
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
    dialog = ft.AlertDialog(title=ft.Text("Окно", size=0, color="#FDD3E8"), bgcolor='#201314', modal=True)

    def close_delete_dialog(e=None):
        if dialog:
            dialog.open = False
            dialog.actions.clear()
            page.update()

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

    def update_input_form():
        result_input_form.controls.clear()
        result_input_form.controls.append(input_form(page, highlighted_books, update_highlighted_books))

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
        update_input_form()

    def delete_highlighted_books():
        nonlocal books, highlighted_books
        delete_books(file_path, highlighted_books.get_books())
        length: int
        try:
            length = len(highlighted_books.get_books())
        except Exception as e:
            length = 0

        dialog.actions.append(delete_dialog_element(length, close_delete_dialog))
        dialog.open = True
        page.open(dialog)
        books = get_books(file_path)
        highlighted_books.books = books
        highlighted_books_parameters_to_none()
        update_highlighted_books()
        close_dialog()

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
                    ft.Text('Удаление книг', size=24, color='#FDD3E8'),
                    ft.Container(expand=1,
                                 content=ft.ElevatedButton(
                                     'Удалить', height=38, width=120, bgcolor='#E54D2E', color='#FDD3E8',
                                     on_click=lambda _: delete_highlighted_books()
                                 ),
                                 alignment=ft.alignment.center_right
                                 )
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