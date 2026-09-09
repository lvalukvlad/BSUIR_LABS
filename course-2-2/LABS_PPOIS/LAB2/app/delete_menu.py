import flet as ft
from typing import List
from source.tournament import Tournament
from source.get_tournaments import get_tournaments
from components.list_of_tournaments import list_of_tournaments
from source.highlighted_tournaments import HighlightedTournaments
from components.pagination import pagination
from source.tournament_page import TournamentPage
from source.delete_tournaments import delete_tournaments
from components.input_form import input_form
from components.error_file_element import error_file_element
from components.delete_dialog_element import delete_dialog_element


def delete_menu(page: ft.Page, file_path: str, close_dialog, highlighted_tournaments: HighlightedTournaments):
    if file_path == '':
        close_dialog()
        return error_file_element(close_dialog)

    tournament_page: TournamentPage = TournamentPage()
    out_tournaments = ft.Column(
        controls=[
            list_of_tournaments(page, highlighted_tournaments.get_tournaments(), tournament_page)
        ]
    )
    dialog = ft.AlertDialog(title=ft.Text("Окно", size=0, color="#FDD3E8"), bgcolor='#201314', modal=True)

    def close_delete_dialog(e=None):
        if dialog:
            dialog.open = False
            dialog.actions.clear()
            page.update()

    def update_list_of_tournaments():
        out_tournaments.controls.clear()
        out_tournaments.controls.append(
            list_of_tournaments(page, highlighted_tournaments.get_tournaments(), tournament_page))
        page.update()

    if highlighted_tournaments.get_tournaments():
        tournaments_container = ft.Column(
            controls=[
                out_tournaments,
                pagination(page, len(highlighted_tournaments.get_tournaments()), tournament_page,
                           update_list_of_tournaments)
            ]
        )
    else:
        tournaments_container = ft.Column(
            controls=[
                out_tournaments,
            ]
        )

    def update_highlighted_tournaments():
        tournaments_container.controls.clear()
        update_list_of_tournaments()
        tournaments_container.controls.append(out_tournaments)
        if highlighted_tournaments.get_tournaments():
            tournaments_container.controls.append(
                pagination(page, len(highlighted_tournaments.get_tournaments()), tournament_page,
                           update_list_of_tournaments))
        page.update()

    result_input_form = ft.Column(
        controls=[input_form(page, highlighted_tournaments, update_highlighted_tournaments)]
    )

    def update_input_form():
        result_input_form.controls.clear()
        result_input_form.controls.append(input_form(page, highlighted_tournaments, update_highlighted_tournaments))

    def highlighted_tournaments_parameters_to_none():
        highlighted_tournaments.set_name('')
        highlighted_tournaments.set_date(None)
        highlighted_tournaments.set_sport_type('')
        highlighted_tournaments.set_winner_name('')
        highlighted_tournaments.set_min_prize_amount(None)
        highlighted_tournaments.set_max_prize_amount(None)
        highlighted_tournaments.set_min_winner_earnings(None)
        highlighted_tournaments.set_max_winner_earnings(None)
        update_input_form()

    def delete_highlighted_tournaments():
        nonlocal highlighted_tournaments
        delete_tournaments(file_path, highlighted_tournaments.get_tournaments())
        length: int
        try:
            length = len(highlighted_tournaments.get_tournaments())
        except Exception as e:
            length = 0

        dialog.actions.append(delete_dialog_element(length, close_delete_dialog))
        dialog.open = True
        page.open(dialog)
        highlighted_tournaments.tournaments = get_tournaments(file_path)
        highlighted_tournaments_parameters_to_none()
        update_highlighted_tournaments()
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
                    ft.Text('Удаление турниров', size=24, color='#FDD3E8'),
                    ft.Container(
                        expand=1,
                        content=ft.ElevatedButton(
                            'Удалить', height=38, width=120, bgcolor='#E54D2E', color='#FDD3E8',
                            on_click=lambda _: delete_highlighted_tournaments()
                        ),
                        alignment=ft.alignment.center_right
                    )
                ],
            ),
            result_input_form,
            tournaments_container
        ],
        width=page.width,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True
    )