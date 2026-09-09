import flet as ft
from sorce.highlighted_books import HighlightedBooks
from sorce.created_book import CreatedBooks
from sorce.debouncer import Debouncer


def create_input_form(
        highlighted_books: HighlightedBooks,
        created_book: CreatedBooks,
        update_highlighted_books
            ):
    debouncer = Debouncer(0.5)
    result_input_form = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.TextField(
                        value=highlighted_books.get_title(),
                        on_change=lambda e: (
                            highlighted_books.set_title(e.control.value),
                            created_book.set_title(e.control.value),
                            debouncer.debounce(update_highlighted_books)
                        ),
                        label="Название книги",
                        hint_text="Название книги",
                        input_filter=ft.InputFilter(
                            allow=True,
                            regex_string=r"^[А-ЯЁа-яё\s-]*$",
                            # regex_string=r"^[А-ЯЁ][а-яё]+([ -][А-ЯЁа-яё][а-яё;:\"',.!?]+){0,7}$",
                            replacement_string=""
                        ),
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
                            created_book.set_author_first_name(e.control.value),
                            debouncer.debounce(update_highlighted_books)
                        ),
                        label="Имя автора",
                        hint_text="Имя автора",
                        input_filter=ft.InputFilter(
                            allow=True,
                            regex_string=r"^[А-ЯЁа-яё\s-]*$",
                            # regex_string=r"^[А-ЯЁ][а-яё]+([-][А-ЯЁ][а-яё]+){0,2}$",
                            replacement_string=""
                        ),
                        max_length=10,
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,
                        border_color="#FFD60A",
                    ),
                    ft.TextField(
                        value=highlighted_books.get_author_last_name(),
                        on_change=lambda e: (
                            highlighted_books.set_author_last_name(e.control.value),
                            created_book.set_author_last_name(e.control.value),
                            debouncer.debounce(update_highlighted_books)
                        ),
                        label="Фамилия автора",
                        hint_text="Фамилия автора",
                        max_length=30,
                        input_filter=ft.InputFilter(
                            allow=True,
                            regex_string=r"^[А-ЯЁа-яё\s-]*$",
                            # regex_string=r"^[А-ЯЁа-яё][а-яё]+([ -][А-ЯЁа-яё][а-яё]+){0,3}$",
                            replacement_string=""
                        ),
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,
                        border_color="#FFD60A",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.TextField(
                            value=highlighted_books.get_min_volumes(),
                            on_change=lambda e: (
                                highlighted_books.set_min_volumes(e.control.value),
                                created_book.set_volumes(e.control.value),
                                debouncer.debounce(update_highlighted_books)
                            ),
                            label="Количество томов",
                            hint_text="Количество томов",
                            input_filter=ft.NumbersOnlyInputFilter(),
                            max_length=3,
                            color='#FDD3E8',
                            cursor_color='#FDD3E8',
                            width=200,
                            border_color="#FFD60A",
                        ),
                    ),
                    ft.TextField(
                        value=highlighted_books.get_publisher(),
                        on_change=lambda e: (
                            highlighted_books.set_publisher(e.control.value),
                            created_book.set_publisher(e.control.value),
                            debouncer.debounce(update_highlighted_books)
                        ),
                        label="Издательство",
                        hint_text="Издательство",
                        input_filter=ft.InputFilter(
                            allow=True,
                            regex_string=r"^[А-ЯЁа-яё\s-]*$",
                            # regex_string=r"^[А-ЯЁ][а-яё]+([ -][А-ЯЁа-яё][а-яё]+){0,4}$",
                            replacement_string=""
                        ),
                        max_length=30,
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,

                        border_color="#FFD60A",
                    ),
                    ft.Container(
                        content=ft.TextField(
                                    value=highlighted_books.get_min_copies(),
                                    on_change=lambda e: (
                                        highlighted_books.set_min_copies(e.control.value),
                                        created_book.set_copies(e.control.value),
                                        debouncer.debounce(update_highlighted_books)
                                    ),
                                    label="Тираж",
                                    hint_text="Тираж",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    max_length=10,
                                    color='#FDD3E8',
                                    cursor_color='#FDD3E8',
                                    width=205,
                                    border_color="#FFD60A",
                                ),
                    ),
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