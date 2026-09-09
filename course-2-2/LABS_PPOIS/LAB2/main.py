import flet as ft
from components.header import header
from app.main_menu import main_menu
from source.get_tournaments import get_tournaments
from app.find_menu import find_menu
from app.delete_menu import delete_menu
from app.create_menu import create_menu
from source.highlighted_tournaments import HighlightedTournaments

def main(page: ft.Page):
    page.title = "Спортивные турниры"
    page.theme_mode = 'dark'
    file_path: str = ''
    tournaments = []
    highlighted_tournaments = HighlightedTournaments(tournaments)
    main_content = ft.Row()
    dialog = None

    def initialize_dialog():
        nonlocal dialog
        if not dialog:
            dialog = ft.AlertDialog(
                title=ft.Text("Окно", size=16, color="#FDD3E8"),
                bgcolor='#201314',
                modal=True,
                actions=[]
            )

    def close_dialog(e=None):
        if dialog and dialog.open:
            dialog.open = False
            dialog.actions.clear()
            show_main_menu()
            page.update()

    def show_main_menu(e=None):
        main_content.controls.clear()
        main_content.controls.append(main_menu(page, file_path, tournaments))
        page.update()

    def show_create_menu(e):
        initialize_dialog()
        dialog.actions.clear()
        dialog.actions.append(create_menu(page, file_path, close_dialog))
        dialog.open = True
        page.open(dialog)

    def show_delete_menu(e):
        initialize_dialog()
        dialog.actions.clear()
        dialog.actions.append(delete_menu(page, file_path, close_dialog, highlighted_tournaments))
        dialog.open = True
        page.open(dialog)

    def show_find_menu(e):
        initialize_dialog()
        dialog.actions.clear()
        dialog.actions.append(find_menu(page, file_path, close_dialog, highlighted_tournaments))
        dialog.open = True
        page.open(dialog)

    def handle_file_selected(origin_file_path: str):
        nonlocal file_path, tournaments, highlighted_tournaments
        file_path = origin_file_path
        try:
            tournaments = get_tournaments(file_path)
            highlighted_tournaments = HighlightedTournaments(tournaments)
            if not tournaments:
                page.snack_bar = ft.SnackBar(ft.Text("Ошибка: файл пуст или повреждён", color="#FF92AD"))
                page.snack_bar.open = True
            show_main_menu()
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка загрузки файла: {e}", color="#FF92AD"))
            page.snack_bar.open = True
        page.update()

    page.appbar = header(
        page,
        show_main_menu,
        show_create_menu,
        show_delete_menu,
        handle_file_selected,
        show_find_menu
    )

    show_main_menu()
    page.add(main_content)

ft.app(target=main)