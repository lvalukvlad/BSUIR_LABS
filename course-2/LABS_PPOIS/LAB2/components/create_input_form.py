import flet as ft
from datetime import datetime, date
from source.debouncer import Debouncer
from source.created_tournament import CreatedTournament
from source.highlighted_tournaments import HighlightedTournaments

def create_input_form(page: ft.Page, highlighted_tournaments: HighlightedTournaments, created_tournament: CreatedTournament, update_callback):
    debouncer = Debouncer(0.5)

    def on_prize_changed(e):
        try:
            value = float(e.control.value) if e.control.value else None
            created_tournament.set_prize_amount(value)
            page.update()
        except ValueError:
            e.control.value = str(created_tournament.get_prize_amount()) if created_tournament.get_prize_amount() is not None else ""
            page.update()

    def on_date_changed(e):
        try:
            if e.control.value:
                selected_date = datetime.strptime(e.control.value, "%Y-%m-%d").date()
                print(f"Manual date input: {selected_date}")
                created_tournament.set_date(selected_date)
            else:
                created_tournament.set_date(None)
            page.update()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            created_tournament.set_date(None)
            page.update()

    def on_field_changed(e, setter):
        setter(e.control.value)
        page.update()

    result_input_form = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.TextField(
                        value=created_tournament.get_name() or "",
                        on_change=lambda e: on_field_changed(e, created_tournament.set_name),
                        label="Название турнира",
                        hint_text="Название турнира",
                        max_length=55,
                        width=250,
                        border_color="#FFD60A",
                    ),
                    ft.TextField(
                        value=str(created_tournament.get_date()) if created_tournament.get_date() else "",
                        on_change=on_date_changed,
                        label="Дата проведения",
                        hint_text="ГГГГ-ММ-ДД (например, 2025-06-04)",
                        width=200,
                        border_color="#FFD60A",
                    ),
                    ft.TextField(
                        value=created_tournament.get_sport_type() or "",
                        on_change=lambda e: on_field_changed(e, created_tournament.set_sport_type),
                        label="Вид спорта",
                        hint_text="Вид спорта",
                        max_length=30,
                        width=200,
                        border_color="#FFD60A",
                        disabled=False,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    ft.TextField(
                        value=created_tournament.get_winner_name() or "",
                        on_change=lambda e: on_field_changed(e, created_tournament.set_winner_name),
                        label="ФИО победителя",
                        max_length=50,
                        width=200,
                        border_color="#FFD60A",
                    ),
                    ft.TextField(
                        value=str(created_tournament.get_prize_amount()) if created_tournament.get_prize_amount() is not None else "",
                        on_change=on_prize_changed,
                        label="Размер призовых турнира",
                        keyboard_type="number",
                        width=200,
                        border_color="#FFD60A",
                        disabled=False,
                    ),
                    ft.TextField(
                        value=str(round(created_tournament.get_prize_amount() * 0.6, 2)) if created_tournament.get_prize_amount() is not None else "",
                        label="Заработок победителя (60%)",
                        width=200,
                        disabled=True,
                        border_color="#FFD60A",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
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