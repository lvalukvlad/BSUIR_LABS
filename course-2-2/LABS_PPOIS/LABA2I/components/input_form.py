import flet as ft
from sorce.highlighted_books import HighlightedBooks
from sorce.debouncer import Debouncer


def input_form(page: ft.Page, highlighted_books: HighlightedBooks,  update_highlighted_books):
    debouncer = Debouncer(0.5)
    result_input_form = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.TextField(
                        value=highlighted_books.get_title(),
                        on_change=lambda e: (
                            highlighted_books.set_title(e.control.value),
                            debouncer.debounce(update_highlighted_books)
                        ),
                        label="Название книги",
                        hint_text="Название книги",
                        max_length=55,
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,

                        border_color="#FFD60A",
                    ),
                    ft.TextField(
                        value=highlighted_books.get_author_first_name(),
                        on_change=lambda e: (
                            highlighted_books.set_author_first_name(e.control.value),
                            debouncer.debounce(update_highlighted_books)
                        ),
                        label="Имя автора",
                        hint_text="Имя автора",
                        max_length=55,
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,
                        border_color="#FFD60A",
                    ),
                    ft.TextField(
                        value=highlighted_books.get_author_last_name(),
                        on_change=lambda e: (
                            highlighted_books.set_author_last_name(e.control.value),
                            debouncer.debounce(update_highlighted_books)
                        ),
                        label="Фамилия автора",
                        hint_text="Фамилия автора",
                        max_length=35,
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,
                        border_color="#FFD60A",
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.TextField(
                                    value=highlighted_books.get_min_volumes(),
                                    on_change=lambda e: (
                                        highlighted_books.set_min_volumes(e.control.value),
                                        debouncer.debounce(update_highlighted_books)
                                    ),
                                    label="Количество томов, от",
                                    hint_text="Количество томов, от",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    max_length=5,
                                    color='#FDD3E8',
                                    cursor_color='#FDD3E8',
                                    width=200,
                                    border_color="#FFD60A",
                                    border_radius=ft.BorderRadius(5, 0, 5, 0),
                                ),
                                ft.TextField(
                                    value=highlighted_books.get_max_volumes(),
                                    on_change=lambda e: (
                                        highlighted_books.set_max_volumes(e.control.value),
                                        debouncer.debounce(update_highlighted_books)
                                    ),
                                    label="Количество глав, до",
                                    hint_text="до",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    max_length=5,
                                    color='#FDD3E8',
                                    cursor_color='#FDD3E8',
                                    width=200,
                                    border_color="#FFD60A",
                                    border_radius=ft.BorderRadius(0, 5, 0, 5)
                                ),
                            ],
                            spacing=0
                        )
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    ft.TextField(
                        value=highlighted_books.get_publisher(),
                        on_change=lambda e: (
                            highlighted_books.set_publisher(e.control.value),
                            debouncer.debounce(update_highlighted_books)
                        ),
                        label="Издательство",
                        hint_text="Издательство",
                        max_length=40,
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,

                        border_color="#FFD60A",
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.TextField(
                                    value=highlighted_books.get_min_copies(),
                                    on_change=lambda e: (
                                        highlighted_books.set_min_copies(e.control.value),
                                        debouncer.debounce(update_highlighted_books)
                                    ),
                                    label="Тираж, от",
                                    hint_text="Тираж, от",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    max_length=13,
                                    color='#FDD3E8',
                                    cursor_color='#FDD3E8',
                                    width=205,
                                    border_color="#FFD60A",
                                    border_radius=ft.BorderRadius(5, 0, 5, 0),
                                ),
                                ft.TextField(
                                    value=highlighted_books.get_max_copies(),
                                    on_change=lambda e: (
                                        highlighted_books.set_max_copies(e.control.value),
                                        debouncer.debounce(update_highlighted_books)
                                    ),
                                    label="Тираж, до",
                                    hint_text="до",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    max_length=13,
                                    color='#FDD3E8',
                                    cursor_color='#FDD3E8',
                                    width=205,
                                    border_color="#FFD60A",
                                    border_radius=ft.BorderRadius(0, 5, 0, 5)
                                ),
                            ],
                            spacing=0
                        )
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.TextField(
                                    value=highlighted_books.get_min_total_volumes(),
                                    on_change=lambda e: (
                                        highlighted_books.set_min_total_volumes(e.control.value),
                                        debouncer.debounce(update_highlighted_books)
                                    ),
                                    label="Итоговый тираж, от",
                                    hint_text="Итоговый тираж, от",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    max_length=65,
                                    color='#FDD3E8',
                                    cursor_color='#FDD3E8',
                                    width=200,
                                    border_color="#FFD60A",
                                    border_radius=ft.BorderRadius(5, 0, 5, 0),
                                ),
                                ft.TextField(
                                    value=highlighted_books.get_max_total_volumes(),
                                    on_change=lambda e: (
                                        highlighted_books.set_max_total_volumes(e.control.value),
                                        debouncer.debounce(update_highlighted_books)
                                    ),
                                    label="Итоговый тираж, до",
                                    hint_text="до",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    max_length=65,
                                    color='#FDD3E8',
                                    cursor_color='#FDD3E8',
                                    width=200,
                                    border_color="#FFD60A",
                                    border_radius=ft.BorderRadius(0, 5, 0, 5)
                                ),
                            ],
                            spacing=0
                        )
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True
    )

    return ft.Container(
        content=result_input_form,
        alignment=ft.alignment.center,
        expand=True
    )