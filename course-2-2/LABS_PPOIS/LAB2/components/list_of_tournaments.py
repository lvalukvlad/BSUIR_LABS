import flet as ft
import math
from source.tournament import Tournament
from typing import List
from source.tournament_page import TournamentPage

def list_of_tournaments(page: ft.Page, tournaments: List[Tournament], tournament_page: TournamentPage):
    if not tournaments:
        return ft.Container(
            content=ft.Text('Не найдены турниры', size=24, color='#FDD3E8'),
            alignment=ft.alignment.center,
            width=page.width
        )

    length: int = len(tournaments)
    max_length: int = math.ceil(length / tournament_page.get_items_per_page())
    tournaments_list = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.ALWAYS,
        height=400,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    def update_page(new_page: int):
        tournaments_list.controls.clear()
        nonlocal max_length
        max_length = math.ceil(length / tournament_page.get_items_per_page())
        start_index = (tournament_page.get_current_page() - 1) * tournament_page.get_items_per_page()
        end_index = start_index + tournament_page.get_items_per_page()
        count: int = 0
        for tournament in tournaments[start_index:end_index]:
            count += 1
            tournament_card = ft.Container(
                content=ft.Column([
                    ft.Text(f"Название: {getattr(tournament, 'name', 'неизвестно')}", size=16, weight=ft.FontWeight.BOLD, color='#FDD3E8'),
                    ft.Text(f"Дата: {getattr(tournament, 'date', 'неизвестно')}", color='#FDD3E8'),
                    ft.Text(f"Спорт: {getattr(tournament, 'sport_type', 'неизвестно')}", color='#FDD3E8'),
                    ft.Text(f"Победитель: {getattr(tournament, 'winner_name', 'неизвестен')}", color='#FDD3E8'),
                    ft.Text(f"Призовой фонд: {getattr(tournament, 'prize_amount', 'неизвестен')}", color='#FDD3E8'),
                    ft.Text(f"Заработок: {getattr(tournament, 'winner_earnings', 'неизвестен')}", color='#FDD3E8')
                ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=3,
                ),
                bgcolor='#4E1325',
                padding=10,
                border_radius=10,
                width=page.width
            )
            tournaments_list.controls.append(tournament_card)

        tournaments_list.controls.append(ft.Text(
            f"Число турниров на странице: {count} "
            f"Доступных страниц: {max_length} "
            f"Число турниров всего: {length}",
            color='#FDD3E8'))
        page.update()

    update_page(tournament_page.get_current_page())
    return ft.Container(
        content=tournaments_list,
        alignment=ft.alignment.center,
        padding=20,
        border_radius=10,
        width=page.width,
    )