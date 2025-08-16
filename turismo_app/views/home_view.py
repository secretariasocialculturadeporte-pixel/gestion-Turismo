import flet as ft

ROUTE_CIUDADANO_TURISMO = "/ciudadano/turismo"
ROUTE_CIUDADANO_EMPLEO = "/ciudadano/empleo"
ROUTE_ADMIN_DASHBOARD = "/admin/dashboard"
ROUTE_LOGIN = "/auth/login"

class HomeView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page

        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20

        welcome_section = self._build_welcome_message()
        action_cards = self._build_action_cards_for_role()

        self.controls = [
            ft.Container(height=self.page.height * 0.1 if self.page.height else 50),
            welcome_section,
            ft.Container(height=self.page.height * 0.05 if self.page.height else 30),
            ft.Text("¿Qué te gustaría hacer hoy?", size=20, weight=ft.FontWeight.W_500, text_align="center"),
            ft.Container(height=15),
            ft.Row(
                action_cards,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
                wrap=True,
                spacing=20,
                run_spacing=20
            ),
        ]

    def _build_welcome_message(self) -> ft.Column:
        user_nombre_completo = self.page.session.get("user_nombre_completo")
        user_rol = self.page.session.get("user_rol")

        if user_nombre_completo:
            return ft.Column(
                [
                    ft.Text(f"¡Bienvenido de nuevo, {user_nombre_completo}!", size=32, weight=ft.FontWeight.BOLD, text_align="center"),
                    ft.Text(f"Rol actual: {user_rol}", size=16, color=ft.colors.SECONDARY, text_align="center"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        else:
            return ft.Column(
                [
                    ft.Text("Bienvenido al Portal de Turismo Territorial", size=32, weight=ft.FontWeight.BOLD, text_align="center"),
                    ft.Text("Descubre, explora y participa en el desarrollo turístico de nuestra región.", size=18, color=ft.colors.OUTLINE, text_align="center"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

    def _build_action_cards_for_role(self) -> list[ft.Card]:
        cards = []
        user_rol = self.page.session.get("user_rol")

        cards.append(
            ft.Card(
                elevation=2.5,
                content=ft.Container(
                    ft.Column([
                        ft.Row([ft.Icon(ft.icons.TRAVEL_EXPLORE_ROUNDED), ft.Text("Explora Destinos", style=ft.TextThemeStyle.TITLE_MEDIUM)]),
                        ft.Text("Descubre atractivos, hoteles, restaurantes y más."),
                        ft.ElevatedButton("Ver Oferta Turística", on_click=lambda _: self.page.go(ROUTE_CIUDADANO_TURISMO))
                    ]),
                    padding=15, width=280
                )
            )
        )

        cards.append(
            ft.Card(
                elevation=2.5,
                content=ft.Container(
                    ft.Column([
                        ft.Row([ft.Icon(ft.icons.WORK_OUTLINE_ROUNDED), ft.Text("Oportunidades de Empleo", style=ft.TextThemeStyle.TITLE_MEDIUM)]),
                        ft.Text("Encuentra vacantes en el sector turístico."),
                        ft.ElevatedButton("Ver Vacantes", on_click=lambda _: self.page.go(ROUTE_CIUDADANO_EMPLEO))
                    ]),
                    padding=15, width=280
                )
            )
        )

        if user_rol and user_rol != "Ciudadano":
            cards.append(
                ft.Card(
                    elevation=2.5,
                    content=ft.Container(
                        ft.Column([
                            ft.Row([ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS_ROUNDED), ft.Text("Panel de Administración", style=ft.TextThemeStyle.TITLE_MEDIUM)]),
                            ft.Text("Accede a las herramientas de gestión."),
                            ft.FilledButton("Ir al Panel Principal", on_click=lambda _: self.page.go(ROUTE_ADMIN_DASHBOARD))
                        ]),
                        padding=15, width=280
                    )
                )
            )

        if not user_rol:
            cards.append(
                ft.Card(
                    elevation=2.5,
                    content=ft.Container(
                        ft.Column([
                            ft.Row([ft.Icon(ft.icons.LOGIN), ft.Text("Acceso a Administradores", style=ft.TextThemeStyle.TITLE_MEDIUM)]),
                            ft.Text("Inicia sesión para acceder a las herramientas."),
                            ft.FilledButton("Iniciar Sesión", on_click=lambda _: self.page.go(ROUTE_LOGIN))
                        ]),
                        padding=15, width=280
                    )
                )
            )

        return cards
