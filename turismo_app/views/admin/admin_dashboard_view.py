import flet as ft

# Mock de rutas
ROUTE_ADMIN_EMPRESAS = "/admin/empresas"
ROUTE_ADMIN_ATRACTIVOS = "/admin/atractivos"
ROUTE_ADMIN_VACANTES = "/admin/vacantes"
ROUTE_ADMIN_USUARIOS = "/admin/usuarios"
ROUTE_ADMIN_REPORTES_NACIONAL = "/admin/reportes/nacional"

class AdminDashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_rol = page.session.get("user_rol")
        self.user_nombre_completo = page.session.get("user_nombre_completo")

        # --- Controles ---
        self.kpi_cards_row = ft.ResponsiveRow(alignment=ft.MainAxisAlignment.CENTER)
        self.accesos_directos_grid = ft.GridView(expand=False, runs_count=5, max_extent=200)

        self._cargar_kpis()
        self._cargar_accesos_directos()

    def build(self):
        return ft.Column(
            [
                ft.Text(f"Bienvenido, {self.user_nombre_completo}", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("Resumen del Sistema", style=ft.TextThemeStyle.TITLE_LARGE),
                self.kpi_cards_row,
                ft.Divider(),
                ft.Text("Módulos de Gestión", style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Container(content=self.accesos_directos_grid)
            ],
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=15,
            padding=25
        )

    def _crear_kpi_card(self, titulo, valor, icono, color):
        return ft.Card(content=ft.Container(padding=15, content=ft.Row([ft.Icon(icono), ft.Column([ft.Text(titulo), ft.Text(valor, size=24)])])))

    def _cargar_kpis(self):
        kpis = [
            {"titulo": "Empresas", "valor": "150", "icono": ft.icons.BUSINESS, "color": ft.colors.BLUE},
            {"titulo": "Atractivos", "valor": "89", "icono": ft.icons.PALETTE, "color": ft.colors.GREEN},
        ]
        self.kpi_cards_row.controls = [ft.Column([self._crear_kpi_card(**k)], col=4) for kpi in kpis]

    def _crear_acceso_directo_card(self, titulo, icono, ruta):
        return ft.Card(content=ft.Container(padding=15, on_click=lambda _: self.page.go(ruta), content=ft.Column([ft.Icon(icono, size=40), ft.Text(titulo)])))

    def _cargar_accesos_directos(self):
        accesos = [
            {"titulo": "Empresas", "icono": ft.icons.STOREFRONT, "ruta": ROUTE_ADMIN_EMPRESAS},
            {"titulo": "Atractivos", "icono": ft.icons.BEACH_ACCESS, "ruta": ROUTE_ADMIN_ATRACTIVOS},
        ]
        if self.user_rol == "SuperAdmin":
            accesos.append({"titulo": "Usuarios", "icono": ft.icons.PEOPLE, "ruta": "/admin/usuarios"})

        self.accesos_directos_grid.controls = [self._crear_acceso_directo_card(**acc) for acc in accesos]
