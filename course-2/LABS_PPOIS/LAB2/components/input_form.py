import flet as ft
from datetime import datetime
from source.highlighted_tournaments import HighlightedTournaments
from source.debouncer import Debouncer

def input_form(page: ft.Page, highlighted_tournaments: HighlightedTournaments, update_highlighted_tournaments):
    debouncer = Debouncer(0.5)
    result_input_form = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.TextField(
                        value=highlighted_tournaments.get_name(),
                        on_change=lambda e: (
                            highlighted_tournaments.set_name(e.control.value),
                            debouncer.debounce(update_highlighted_tournaments)
                        ),
                        label="Название турнира",
                        hint_text="Название турнира",
                        max_length=55,
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,
                        border_color="#FFD60A",
                    ),
                    ft.Container(
                        width=400,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=200,
                                    content=ft.DatePicker(
                                        value=highlighted_tournaments.get_min_date(),
                                        on_change=lambda e: (
                                            highlighted_tournaments.set_date(e.control.value),
                                            debouncer.debounce(update_highlighted_tournaments)
                                        ),
                                        first_date=datetime(2000, 1, 1),
                                        last_date=datetime.now(),
                                        field_label_text="Дата, от",
                                        field_hint_text="Дата, от",
                                    )
                                ),
                                ft.Container(
                                    width=200,
                                    content=ft.DatePicker(
                                        value=highlighted_tournaments.get_max_date(),
                                        on_change=lambda e: (
                                            highlighted_tournaments.set_date(e.control.value),
                                            debouncer.debounce(update_highlighted_tournaments)
                                        ),
                                        first_date=datetime(2000, 1, 1),
                                        last_date=datetime.now(),
                                        field_label_text="Дата, до",
                                        field_hint_text="Дата, до",
                                    )
                                ),
                            ],
                            spacing=0
                        )
                    ),
                    ft.TextField(
                        value=highlighted_tournaments.get_sport_type(),
                        on_change=lambda e: (
                            highlighted_tournaments.set_sport_type(e.control.value),
                            debouncer.debounce(update_highlighted_tournaments)
                        ),
                        label="Вид спорта",
                        hint_text="Вид спорта",
                        max_length=30,
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
                    ft.TextField(
                        value=highlighted_tournaments.get_winner_name(),
                        on_change=lambda e: (
                            highlighted_tournaments.set_winner_name(e.control.value),
                            debouncer.debounce(update_highlighted_tournaments)
                        ),
                        label="ФИО победителя",
                        hint_text="ФИО победителя",
                        max_length=50,
                        color='#FDD3E8',
                        cursor_color='#FDD3E8',
                        width=200,
                        border_color="#FFD60A",
                    ),
                    ft.Container(
                        width=400,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=200,
                                    content=ft.TextField(
                                        value=str(highlighted_tournaments.get_min_prize_amount()) if highlighted_tournaments.get_min_prize_amount() is not None else "",
                                        on_change=lambda e: (
                                            highlighted_tournaments.set_min_prize_amount(float(e.control.value) if e.control.value else None),
                                            debouncer.debounce(update_highlighted_tournaments)
                                        ),
                                        label="Призовой фонд, от",
                                        hint_text="Призовой фонд, от",
                                        input_filter=ft.InputFilter(regex_string=r"^[0-9]*\.?[0-9]*$"),
                                        max_length=10,
                                        color='#FDD3E8',
                                        cursor_color='#FDD3E8',
                                        width=200,
                                        border_color="#FFD60A",
                                        border_radius=ft.BorderRadius(5, 0, 5, 0),
                                    )
                                ),
                                ft.Container(
                                    width=200,
                                    content=ft.TextField(
                                        value=str(highlighted_tournaments.get_max_prize_amount()) if highlighted_tournaments.get_max_prize_amount() is not None else "",
                                        on_change=lambda e: (
                                            highlighted_tournaments.set_max_prize_amount(float(e.control.value) if e.control.value else None),
                                            debouncer.debounce(update_highlighted_tournaments)
                                        ),
                                        label="Призовой фонд, до",
                                        hint_text="Призовой фонд, до",
                                        input_filter=ft.InputFilter(regex_string=r"^[0-9]*\.?[0-9]*$"),
                                        max_length=10,
                                        color='#FDD3E8',
                                        cursor_color='#FDD3E8',
                                        width=200,
                                        border_color="#FFD60A",
                                        border_radius=ft.BorderRadius(0, 5, 0, 5),
                                    )
                                ),
                            ],
                            spacing=0
                        )
                    ),
                    ft.Container(
                        width=400,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=200,
                                    content=ft.TextField(
                                        value=str(highlighted_tournaments.get_min_winner_earnings()) if highlighted_tournaments.get_min_winner_earnings() is not None else "",
                                        on_change=lambda e: (
                                            highlighted_tournaments.set_min_winner_earnings(float(e.control.value) if e.control.value else None),
                                            debouncer.debounce(update_highlighted_tournaments)
                                        ),
                                        label="Заработок, от",
                                        hint_text="Заработок, от",
                                        input_filter=ft.InputFilter(regex_string=r"^[0-9]*\.?[0-9]*$"),
                                        max_length=10,
                                        color='#FDD3E8',
                                        cursor_color='#FDD3E8',
                                        width=200,
                                        border_color="#FFD60A",
                                        border_radius=ft.BorderRadius(5, 0, 5, 0),
                                    )
                                ),
                                ft.Container(
                                    width=200,
                                    content=ft.TextField(
                                        value=str(highlighted_tournaments.get_max_winner_earnings()) if highlighted_tournaments.get_max_winner_earnings() is not None else "",
                                        on_change=lambda e: (
                                            highlighted_tournaments.set_max_winner_earnings(float(e.control.value) if e.control.value else None),
                                            debouncer.debounce(update_highlighted_tournaments)
                                        ),
                                        label="Заработок, до",
                                        hint_text="Заработок, до",
                                        input_filter=ft.InputFilter(regex_string=r"^[0-9]*\.?[0-9]*$"),
                                        max_length=10,
                                        color='#FDD3E8',
                                        cursor_color='#FDD3E8',
                                        width=200,
                                        border_color="#FFD60A",
                                        border_radius=ft.BorderRadius(0, 5, 0, 5),
                                    )
                                ),
                            ],
                            spacing=0
                        )
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