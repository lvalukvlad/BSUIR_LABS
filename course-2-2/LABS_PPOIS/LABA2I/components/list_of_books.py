import flet as ft
import math
from sorce.book import Book
from typing import List
from sorce.book_page import BookPage


def list_of_books(page: ft.Page, books: List[Book], book_page: BookPage):
    if not books:
        return ft.Container(
            content=ft.Text('Не найдены книги', size=24, color='#FDD3E8'),
            alignment=ft.alignment.center,
            width=page.width
        )
    length: int = len(books)
    max_length: int = math.ceil(length / book_page.get_items_per_page())
    books_list = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.ALWAYS,
        height=250,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    def update_page(new_page: int):
        books_list.controls.clear()
        nonlocal max_length
        max_length = math.ceil(length / book_page.get_items_per_page())
        start_index = (book_page.get_current_page() - 1) * book_page.get_items_per_page()
        end_index = start_index + book_page.get_items_per_page()
        count: int = 0
        for book in books[start_index:end_index]:
            count += 1
            book_card = ft.Container(
                content=ft.Row([
                    ft.Text(f"Название: {book['title']}", size=16, weight=ft.FontWeight.BOLD, color='#FDD3E8'),
                    ft.Text(f"Автор: {book['author']}", color='#FDD3E8'),
                    ft.Text(f"Издательство: {book['publisher']}", color='#FDD3E8'),
                    ft.Text(f"Томов: {book['volumes']}", color='#FDD3E8'),
                    ft.Text(f"Тираж: {book['copies']}", color='#FDD3E8'),
                    ft.Text(f"Итого томов: {book['total_volumes']}", color='#FDD3E8')
                ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=3,
                    scroll=ft.ScrollMode.AUTO,
                ),
                bgcolor='#4E1325',
                padding=10,
                border_radius=10,
                width=page.width
            )
            books_list.controls.append(book_card)
        books_list.controls.append(ft.Text(
            f" Число книг на странице {count} "
            f"Доступных страниц: {math.ceil(length / book_page.get_items_per_page())} "
            f"Число книг всего: {length}",
            color='#FDD3E8'))
        page.update()
    update_page(book_page.get_current_page())
    return ft.Container(
        content=books_list,
        alignment=ft.alignment.center,
        padding=20,
        border_radius=10,
        width=page.width,
    )