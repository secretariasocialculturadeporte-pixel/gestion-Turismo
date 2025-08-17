import flet as ft

class RestauranteAdminPanelView:
    def __init__(self, page: ft.Page):
        self.page = page

    def _crear_acceso_directo(self, titulo, icono, ruta):
        return ft.Card(
            elevation=2,
            content=ft.Container(
                width=200,
                height=150,
                padding=15,
                on_click=lambda _: self.page.go(ruta),
                ink=True,
                content=ft.Column(
                    [
                        ft.Icon(icono, size=40),
                        ft.Text(titulo, weight=ft.FontWeight.BOLD, text_align="center"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            )
        )

    def build(self):
        return ft.Column(
            [
                ft.Text("Panel de Administración del Restaurante", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row(
                    controls=[
                        self._crear_acceso_directo(
                            "Gestionar Menú",
                            ft.icons.MENU_BOOK,
                            "/empresa/restaurante/menu"
                        ),
                        self._crear_acceso_directo(
                            "Configurar Mesas",
                            ft.icons.TABLE_RESTAURANT,
                            "/empresa/restaurante/mesas"
                        ),
                        self._crear_acceso_directo(
                            "Ver Informes",
                            ft.icons.INSIGHTS,
                            "/empresa/restaurante/informes"
                        ),
                    ],
                    wrap=True,
                    spacing=20,
                    run_spacing=20
                )
            ]
        )
