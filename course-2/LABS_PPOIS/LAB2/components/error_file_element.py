import flet as ft


def error_file_element(close_dialog):
    return ft.Row(
        controls=[
            ft.Container(
                expand=1,
                content=ft.ElevatedButton(
                    "Закрыть", color="#FDD3E8", on_click=close_dialog, height=38, width=120,
                ),
                alignment=ft.alignment.center_left
            ),
            ft.Text('Добавьте файл', size=24, color='#FDD3E8'),
            ft.Container(
                expand=1,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )