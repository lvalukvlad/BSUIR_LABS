import flet as ft


def header(page: ft.Page, show_main_menu, show_create_menu, show_delete_menu, on_file_selected, show_find_menu):
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            on_file_selected(e.files[0].path)
            page.update()
        #     tree = ET.parse(e.files[0].path)
        #     root = tree.getroot()
        #     for book in root.findall('book'):
        #         title = book.find('title').text
        #         author = book.find('author').text
        #         publisher = book.find('publisher').text
        #         volumes = book.find('volumes').text
        #         copies = book.find('copies').text
        #         print(f"""
        #         Название: {title}
        #         Автор: {author}
        #         Издательство: {publisher}
        #         Томов: {volumes}
        #         Тираж: {copies}
        #         """)

    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)
    return ft.AppBar(
        bgcolor='#433500',
        color='#FDD3E8',
        center_title=True,
        leading=ft.Container(
            content=ft.IconButton(
                icon=ft.icons.FILE_UPLOAD,
                tooltip="Загрузить XML файл",
                on_click=lambda _: file_picker.pick_files(allowed_extensions=["xml"]),
            )
        ),
        title=ft.Row(
            controls=[
                ft.IconButton(icon=ft.icons.HOME, tooltip="Главное меню", on_click=show_main_menu),
                ft.IconButton(icon=ft.icons.FIND_IN_PAGE_ROUNDED, tooltip="Найти", on_click=show_find_menu),
                ft.IconButton(icon=ft.icons.ADD, tooltip="Добавить", on_click=show_create_menu),
                ft.IconButton(icon=ft.icons.DELETE, tooltip="Удалить", on_click=show_delete_menu),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
    )