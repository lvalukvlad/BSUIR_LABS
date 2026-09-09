import flet as ft
from typing import List
from source.tournament import Tournament
from source.get_tournaments import get_tournaments
from components.list_of_tournaments import list_of_tournaments
from source.highlighted_tournaments import HighlightedTournaments
from components.pagination import pagination
from source.tournament_page import TournamentPage
from source.create_tournament import create_tournament
from components.create_input_form import create_input_form
from source.created_tournament import CreatedTournament
from source.delete_tournaments import delete_tournaments
from source.validate_create_tournament import validate_create_tournament
from components.error_file_element import error_file_element

def create_menu(page: ft.Page, file_path: str, close_dialog):
    if file_path == '':
        close_dialog()
        return error_file_element(close_dialog)

    tournaments: List[Tournament] = get_tournaments(file_path)
    tournament_page: TournamentPage = TournamentPage()
    highlighted_tournaments: HighlightedTournaments = HighlightedTournaments(tournaments)
    created_tournament: CreatedTournament = CreatedTournament()
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
            ft.Text(value=f"{error_value}", color='#E54D2E')
        )
        page.update()

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
                pagination(page, len(highlighted_tournaments.get_tournaments()), tournament_page, update_list_of_tournaments)
            ],
            spacing=20
        )
    else:
        tournaments_container = ft.Column(
            controls=[
                out_tournaments,
            ],
            spacing=10
        )

    def update_highlighted_tournaments():
        nonlocal error_value
        error_value = ''
        tournaments_container.controls.clear()
        update_list_of_tournaments()
        tournaments_container.controls.append(out_tournaments)
        if highlighted_tournaments.get_tournaments():
            tournaments_container.controls.append(
                pagination(page, len(highlighted_tournaments.get_tournaments()), tournament_page, update_list_of_tournaments))
        if not error_value:
            error_value = ''
            update_error()
        page.update()

    result_input_form = ft.Container(
        content=ft.Column(
            controls=[create_input_form(page, highlighted_tournaments, created_tournament, update_highlighted_tournaments)],
            spacing=10,
        ),
        padding=10,
        bgcolor='#FFFFFF',
        border_radius=10,
        margin=ft.margin.only(bottom=20),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color="#33000000",
            offset=ft.Offset(0, 5)
        )
    )

    def update_input_form():
        result_input_form.content.controls.clear()
        result_input_form.content.controls.append(
            create_input_form(page, highlighted_tournaments, created_tournament, update_highlighted_tournaments)
        )
        page.update()

    def create_tournament_parameters_to_none():
        nonlocal created_tournament
        created_tournament.set_name(None)
        created_tournament.set_date(None)
        created_tournament.set_sport_type(None)
        created_tournament.set_winner_name(None)
        created_tournament.set_prize_amount(None)

    def highlighted_tournaments_parameters_to_none():
        highlighted_tournaments.set_name(None)
        highlighted_tournaments.set_date(None)
        highlighted_tournaments.set_sport_type(None)
        highlighted_tournaments.set_winner_name('')
        highlighted_tournaments.set_min_prize_amount(None)
        highlighted_tournaments.set_max_prize_amount(None)
        highlighted_tournaments.set_min_winner_earnings(None)
        highlighted_tournaments.set_max_winner_earnings(None)
        create_tournament_parameters_to_none()
        update_input_form()

    def create_highlighted_tournaments():
        nonlocal tournaments, highlighted_tournaments, created_tournament, error_value
        print(f"Name: {created_tournament.get_name()}")
        print(f"Date: {created_tournament.get_date()}")
        print(f"Sport Type: {created_tournament.get_sport_type()}")
        print(f"Winner Name: {created_tournament.get_winner_name()}")
        print(f"Prize Amount: {created_tournament.get_prize_amount()}")

        if created_tournament.get_tournament():
            error_value = validate_create_tournament(created_tournament)
            if error_value:
                update_error()
                return
            for tournament in tournaments:
                if (
                    created_tournament.get_name() == tournament.name and
                    created_tournament.get_sport_type() == tournament.sport_type and
                    created_tournament.get_winner_name() == tournament.winner_name
                ):
                    delete_tournaments(file_path, [created_tournament.get_tournament()])
            create_tournament(file_path, created_tournament.get_tournament())
            new_tournaments = get_tournaments(file_path)
            highlighted_tournaments.tournaments = new_tournaments
            tournaments = new_tournaments
            highlighted_tournaments_parameters_to_none()
            update_highlighted_tournaments()
            page.update()
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
                                "Закрыть",
                                color="#FFFFFF",
                                bgcolor="#FF6B6B",
                                height=40,
                                width=120,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=5,
                                    animation_duration=300,
                                    color={
                                        ft.ControlState.HOVERED: "#FFFFFF",
                                        ft.ControlState.DEFAULT: "#FFFFFF",
                                    },
                                    bgcolor={
                                        ft.ControlState.HOVERED: "#FF8787",
                                        ft.ControlState.DEFAULT: "#FF6B6B",
                                    }
                                ),
                                on_click=lambda _: (close_dialog(), page.update())
                            ),
                            alignment=ft.alignment.center_left
                        ),
                        ft.Text('Создание турниров', size=28, color='#4A90E2', weight=ft.FontWeight.BOLD),
                        ft.Container(
                            expand=1,
                            content=ft.ElevatedButton(
                                'Создание',
                                height=40,
                                width=120,
                                bgcolor='#4A90E2',
                                color='#FFFFFF',
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=5,
                                    animation_duration=300,
                                    color={
                                        ft.ControlState.HOVERED: "#FFFFFF",
                                        ft.ControlState.DEFAULT: "#FFFFFF",
                                    },
                                    bgcolor={
                                        ft.ControlState.HOVERED: "#6AA8E8",
                                        ft.ControlState.DEFAULT: "#4A90E2",
                                    }
                                ),
                                on_click=lambda _: create_highlighted_tournaments()
                            ),
                            alignment=ft.alignment.center_right
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                error,
                result_input_form,
                tournaments_container
            ],
            width=page.width,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            spacing=20
        ),
        bgcolor='#F5F7FA',
        padding=30
    )