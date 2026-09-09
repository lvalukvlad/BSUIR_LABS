import flet as ft
from source.tournament import Tournament
from components.list_of_tournaments import list_of_tournaments
from components.pagination import pagination
from source.tournament_page import TournamentPage

def main_menu(page: ft.Page, file_path: str, tournaments: list):
    if file_path == '':
        return ft.Container(
            content=ft.Text('Добавьте файл', size=24, color='#FDD3E8'),
            alignment=ft.alignment.center,
            width=page.width
        )

    if not tournaments:
        return ft.Container(
            content=ft.Text('Нет данных о турнирах в файле', size=24, color='#FF92AD'),
            alignment=ft.alignment.center,
            width=page.width
        )

    tournament_page: TournamentPage = TournamentPage()
    out_tournaments = ft.Column(
        controls=[
            list_of_tournaments(page, tournaments, tournament_page)
        ]
    )

    def update_output_tournaments():
        out_tournaments.controls.clear()
        out_tournaments.controls.append(list_of_tournaments(page, tournaments, tournament_page))
        page.update()

    tournaments_container = ft.Column(
        controls=[
            out_tournaments,
            pagination(page, len(tournaments), tournament_page, update_output_tournaments)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Text('Главное меню', size=24, color='#FDD3E8'),
                alignment=ft.alignment.center,
                width=page.width
            ),
            tournaments_container,
        ],
        width=page.width,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True
    )