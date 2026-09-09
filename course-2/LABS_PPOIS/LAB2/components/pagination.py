import flet as ft
import math


def pagination(page: ft.Page, length: int, tournament_page, update_output):
    max_length = math.ceil(length / tournament_page.get_items_per_page())

    def new_current_page(current_page: int):
        if 0 < current_page <= max_length:
            tournament_page.set_current_page(current_page)
            current_button.value = str(current_page)
            update_output()
        page.update()

    def on_page_submit(e):
        try:
            new_page = int(current_button.value)
            if 0 < new_page <= max_length:
                new_current_page(new_page)
            else:
                raise ValueError
        except ValueError:
            current_button.value = str(tournament_page.get_current_page())
        page.update()

    def on_per_page_submit(e):
        try:
            new_per_page = int(per_page_button.value)
            if new_per_page > 0:
                tournament_page.set_items_per_page(new_per_page)
                new_current_page(1)
                per_page_button.value = str(new_per_page)
                update_output()
            else:
                raise ValueError
        except ValueError:
            per_page_button.value = str(tournament_page.get_items_per_page())
        page.update()

    first_button = ft.IconButton(
        icon="first_page",
        icon_color='#FF92AD',
        tooltip="Первая страница",
        on_click=lambda _: new_current_page(1)
    )
    last_button = ft.IconButton(
        icon="last_page",
        icon_color='#FF92AD',
        tooltip="Последняя страница",
        on_click=lambda _: new_current_page(max_length)
    )
    prev_button = ft.IconButton(
        icon="arrow_back",
        icon_color='#FDD3E8',
        tooltip="Предыдущая страница",
        on_click=lambda _: new_current_page(tournament_page.get_current_page() - 1)
    )
    next_button = ft.IconButton(
        icon="arrow_forward",
        icon_color='#FDD3E8',
        tooltip="Следующая страница",
        on_click=lambda _: new_current_page(tournament_page.get_current_page() + 1)
    )
    current_button = ft.TextField(
        value=str(tournament_page.get_current_page()),
        width=50,
        color='#FDD3E8',
        text_align=ft.TextAlign.CENTER,
        on_submit=on_page_submit
    )
    per_page_button = ft.TextField(
        value=str(tournament_page.get_items_per_page()),
        color='#FDD3E8',
        width=50,
        text_align=ft.TextAlign.CENTER,
        on_submit=on_per_page_submit
    )

    new_current_page(1)

    navigation = ft.Row(
        controls=[
            first_button,
            prev_button,
            current_button,
            ft.Text('(', size=24, weight=ft.FontWeight.BOLD, color='#FF92AD'),
            per_page_button,
            ft.Text(')', size=24, weight=ft.FontWeight.BOLD, color='#FF92AD'),
            next_button,
            last_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    navigation_container = ft.Container(
        content=navigation,
        alignment=ft.alignment.center,
        width=page.width,
    )
    return ft.Container(
        content=ft.Column(
            [
                navigation_container
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        alignment=ft.alignment.center,
        padding=20,
        border_radius=10,
        margin=10,
        width=page.width,
    )
