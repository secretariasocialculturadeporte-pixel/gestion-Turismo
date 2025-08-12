import flet as ft

# Asumimos que las constantes de ruta están en main.py y las importamos o replicamos
# from ..main import ROUTE_CIUDADANO_TURISMO, ROUTE_CIUDADANO_EMPLEO, ROUTE_ADMIN_DASHBOARD, ROUTE_LOGIN
# Si no puedes importarlas directamente desde main (dependencia circular), defínelas aquí o en un archivo de constantes.
ROUTE_CIUDADANO_TURISMO = "/ciudadano/turismo"
ROUTE_CIUDADANO_EMPLEO = "/ciudadano/empleo"
ROUTE_ADMIN_DASHBOARD = "/admin/dashboard"
ROUTE_LOGIN = "/auth/login"


class HomeView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page

    def _build_welcome_message(self) -> ft.Control:
        user_nombre_completo = self.page.session.get("user_nombre_completo")
        user_rol = self.page.session.get("user_rol")

        if user_nombre_completo:
            return ft.Column(
                [
                    ft.Text(f"¡Bienvenido de nuevo, {user_nombre_completo}!", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Rol actual: {user_rol}", size=16, color=ft.colors.SECONDARY, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        else:
            return ft.Column(
                [
                    ft.Text("Bienvenido al Portal de Turismo Territorial", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text("Descubre, explora y participa en el desarrollo turístico de nuestra región.", size=18, color=ft.colors.OUTLINE, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

    def _build_action_cards_for_role(self) -> list[ft.Control]:
        cards = []
        user_rol = self.page.session.get("user_rol")

        # --- Acciones para CIUDADANO (registrado o no) ---
        cards.append(
            ft.Card(
                elevation=2.5,
                content=ft.Container(
                    ft.Column([
                        ft.Row([ft.Icon(ft.icons.TRAVEL_EXPLORE_ROUNDED, size=28, color=ft.colors.PRIMARY), ft.Text("Explora Destinos", style=ft.TextThemeStyle.TITLE_MEDIUM)]),
                        ft.Text("Descubre atractivos, hoteles, restaurantes y más en nuestros municipios.", size=14, color=ft.colors.ON_SURFACE_VARIANT),
                        ft.Container(height=10),
                        ft.ElevatedButton("Ver Oferta Turística", icon=ft.icons.LOCATION_SEARCH_ROUNDED, on_click=lambda _: self.page.go(ROUTE_CIUDADANO_TURISMO), width=250, height=40)
                    ]),
                    padding=20,
                    width=320
                )
            )
        )
        cards.append(
            ft.Card(
                elevation=2.5,
                content=ft.Container(
                    ft.Column([
                        ft.Row([ft.Icon(ft.icons.WORK_OUTLINE_ROUNDED, size=28, color=ft.colors.PRIMARY), ft.Text("Oportunidades de Empleo", style=ft.TextThemeStyle.TITLE_MEDIUM)]),
                        ft.Text("Encuentra vacantes en el sector turístico y forma parte de su crecimiento.", size=14, color=ft.colors.ON_SURFACE_VARIANT),
                        ft.Container(height=10),
                        ft.ElevatedButton("Ver Vacantes", icon=ft.icons.FIND_IN_PAGE_ROUNDED, on_click=lambda _: self.page.go(ROUTE_CIUDADANO_EMPLEO), width=250, height=40)
                    ]),
                    padding=20,
                    width=320
                )
            )
        )

        # --- Acciones para ROLES ADMIN ---
        if user_rol and user_rol != "Ciudadano":
            cards.append(
                ft.Card(
                    elevation=2.5,
                    content=ft.Container(
                        ft.Column([
                            ft.Row([ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS_ROUNDED, size=28, color=ft.colors.TERTIARY), ft.Text("Panel de Administración", style=ft.TextThemeStyle.TITLE_MEDIUM)]),
                            ft.Text("Accede a las herramientas de gestión y reportes correspondientes a tu rol.", size=14, color=ft.colors.ON_SURFACE_VARIANT),
                            ft.Container(height=10),
                            ft.FilledButton("Ir al Panel Principal", icon=ft.icons.DASHBOARD_CUSTOMIZE_ROUNDED, on_click=lambda _: self.page.go(ROUTE_ADMIN_DASHBOARD), width=250, height=40)
                        ]),
                        padding=20,
                        width=320
                    )
                )
            )

        # --- Acción si NO está logueado ---
        if not user_rol:
            cards.append(
                ft.Card(
                    elevation=2.5,
                    content=ft.Container(
                        ft.Column([
                            ft.Row([ft.Icon(ft.icons.LOGIN_ROUNDED, size=28, color=ft.colors.TERTIARY), ft.Text("Acceso a Administradores", style=ft.TextThemeStyle.TITLE_MEDIUM)]),
                            ft.Text("Si eres un gestor territorial o administrador del sistema, inicia sesión para acceder a las herramientas.", size=14, color=ft.colors.ON_SURFACE_VARIANT),
                            ft.Container(height=10),
                            ft.FilledButton("Iniciar Sesión", icon=ft.icons.LOGIN, on_click=lambda _: self.page.go(ROUTE_LOGIN), width=250, height=40)
                        ]),
                        padding=20,
                        width=320
                    )
                )
            )

        return cards

    def build(self):
        welcome_section = self._build_welcome_message()
        action_cards = self._build_action_cards_for_role()

        main_content_column = ft.Column(
            [
                ft.Container(height=self.page.height * 0.1 if self.page.height else 50), # Espacio superior
                welcome_section,
                ft.Container(height=self.page.height * 0.05 if self.page.height else 30),
                ft.Text("¿Qué te gustaría hacer hoy?", size=20, weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                ft.Container(height=15),
                ft.Row(
                    action_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    wrap=True,
                    spacing=20,
                    run_spacing=20
                ),
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    ft.colors.with_opacity(0.1, self.page.theme.color_scheme.primary_container if self.page.theme else ft.colors.BLUE_GREY_50),
                    ft.colors.with_opacity(0.01, self.page.theme.color_scheme.surface if self.page.theme else ft.colors.WHITE),
                ]
            ),
            content=main_content_column,
            expand=True,
            padding=ft.padding.symmetric(vertical=30, horizontal=15),
            alignment=ft.alignment.top_center
        )
