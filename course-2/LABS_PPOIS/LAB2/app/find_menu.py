import flet as ft
from typing import List
from source.tournament import Tournament
from source.get_tournaments import get_tournaments
from components.list_of_tournaments import list_of_tournaments
from source.highlighted_tournaments import HighlightedTournaments
from components.pagination import pagination
from source.tournament_page import TournamentPage
from components.input_form import input_form
from components.error_file_element import error_file_element


def find_menu(page: ft.Page, file_path: str, close_dialog, highlighted_tournaments: HighlightedTournaments):
    if file_path == '':
        close_dialog()
        return error_file_element(close_dialog)

    tournament_page: TournamentPage = TournamentPage()
    out_tournaments = ft.Column(
        controls=[
            list_of_tournaments(page, highlighted_tournaments.get_tournaments(), tournament_page)
        ]
    )

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
                    ft.Text('Поиск турниров', size=24, color='#FDD3E8'),
                    ft.Container(expand=1)
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