import flet as ft

def header(page: ft.Page, show_main_menu, show_create_menu, show_delete_menu, on_file_selected, show_find_menu):
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            on_file_selected(e.files[0].path)
            page.update()

    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)
    return ft.AppBar(
        bgcolor='#433500',
        color='#FDD3E8',
        center_title=True,
        leading=ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.FILE_UPLOAD,
                tooltip="Загрузить XML файл",
                on_click=lambda _: file_picker.pick_files(allowed_extensions=["xml"]),
            )
        ),
        title=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.HOME, tooltip="Главное меню", on_click=show_main_menu),
                ft.IconButton(icon=ft.Icons.FIND_IN_PAGE_ROUNDED, tooltip="Найти", on_click=show_find_menu),
                ft.IconButton(icon=ft.Icons.ADD, tooltip="Добавить", on_click=show_create_menu),
                ft.IconButton(icon=ft.Icons.DELETE, tooltip="Удалить", on_click=show_delete_menu),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
    )
