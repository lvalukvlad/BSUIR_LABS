import flet as ft
from components.header import header
from app.main_menu import main_menu
from sorce.get_books import get_books
from app.find_menu import find_menu
from app.delete_menu import delete_menu
from app.create_menu import create_menu


def main(page: ft.Page):
    page.title = "ППОИС-лабораторная-2"
    page.theme_mode = 'black'
    file_path: str = ''

    main_content = ft.Row()
    dialog = ft.AlertDialog(title=ft.Text("Окно", size=0, color="#FDD3E8"), bgcolor='#201314', modal=True)

    def close_dialog(e=None):
        if dialog:
            dialog.open = False
            dialog.actions.clear()
            show_main_menu()
            page.update()

    def show_main_menu(e=None):
        main_content.controls.clear()
        main_content.controls.append(main_menu(page, file_path))
        page.update()

    def show_create_menu(e):
        dialog.actions.append(create_menu(page, file_path, close_dialog))
        dialog.open = True
        page.open(dialog)

    def show_delete_menu(e):
        dialog.actions.append(delete_menu(page, file_path, close_dialog))
        dialog.open = True
        page.open(dialog)

    def show_find_menu(e):
        dialog.actions.append(find_menu(page, file_path, close_dialog))
        dialog.open = True
        page.open(dialog)

    def handle_file_selected(origin_file_path: str):
        nonlocal file_path
        file_path = origin_file_path
        books = get_books(file_path)
        show_main_menu()
        page.update()

    page.appbar = header(
        page,
        show_main_menu,
        show_create_menu,
        show_delete_menu,
        handle_file_selected,
        show_find_menu)

    main_content.controls.append(main_menu(page, file_path))
    page.add(main_content)


ft.app(target=main)