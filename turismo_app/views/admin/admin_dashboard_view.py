import flet as ft
from turismo_app.database import db_manager

# Mock de rutas, deberían estar en un archivo central
ROUTE_ADMIN_ATRACTIVOS = "/admin/atractivos"
ROUTE_ADMIN_EMPRESAS = "/admin/empresas"
ROUTE_ADMIN_VACANTES = "/admin/vacantes"
ROUTE_ADMIN_INICIATIVAS = "/admin/iniciativas"
ROUTE_ADMIN_DIAGNOSTICO = "/admin/diagnostico"
ROUTE_ADMIN_ENCUESTAS = "/admin/encuestas"
ROUTE_ADMIN_INDICADORES = "/admin/indicadores"
ROUTE_ADMIN_USUARIOS = "/admin/usuarios"
ROUTE_ADMIN_REPORTES_MUNICIPIO = "/admin/reportes/municipio"
ROUTE_ADMIN_REPORTES_DEPARTAMENTO = "/admin/reportes/departamento"
ROUTE_ADMIN_REPORTES_NACIONAL = "/admin/reportes/nacional"

class AdminDashboardView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.user_rol = page.session.get("user_rol")
        self.user_nombre_completo = page.session.get("user_nombre_completo")
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.codigo_departamento_admin = page.session.get("user_codigo_departamento")

        # --- Controles para KPIs ---
        self.kpi_cards_row = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # --- Controles para Accesos Directos ---
        self.accesos_directos_grid = ft.GridView(
            expand=False,
            runs_count=5,  # ~5 columnas en pantalla ancha, se ajustará
            max_extent=200, # Ancho máximo de cada tarjeta
            child_aspect_ratio=1.2, # Relación ancho/alto
            spacing=15,
            run_spacing=15,
            padding=10
        )

    def did_mount(self):
        self._cargar_kpis()
        self._cargar_accesos_directos()

    def _crear_kpi_card(self, titulo, valor, icono, color_valor):
        return ft.Card(
            elevation=2,
            content=ft.Container(
                padding=15,
                content=ft.Row(
                    [
                        ft.Icon(icono, size=35, opacity=0.7),
                        ft.Column(
                            [
                                ft.Text(titulo, size=14, color=ft.colors.OUTLINE),
                                ft.Text(valor, size=24, weight=ft.FontWeight.BOLD, color=color_valor),
                            ],
                            spacing=2
                        )
                    ],
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )

    def _cargar_kpis(self):
        self.kpi_cards_row.controls.clear()
        # Lógica para cargar KPIs desde db_manager (simulado por ahora)

        # Ejemplo de KPI
        kpi1 = self._crear_kpi_card("Empresas Registradas", "150", ft.icons.BUSINESS_CENTER, ft.colors.BLUE_700)
        kpi2 = self._crear_kpi_card("Atractivos Inventariados", "89", ft.icons.PALETTE, ft.colors.GREEN_700)
        kpi3 = self._crear_kpi_card("Vacantes Activas", "12", ft.icons.WORK, ft.colors.ORANGE_700)

        self.kpi_cards_row.controls.extend([
             ft.Column([kpi1], col={"sm": 6, "md": 4, "xl": 2}),
             ft.Column([kpi2], col={"sm": 6, "md": 4, "xl": 2}),
             ft.Column([kpi3], col={"sm": 6, "md": 4, "xl": 2}),
        ])
        self.update()

    def _crear_acceso_directo_card(self, titulo, icono, ruta, descripcion, color_icono):
        return ft.Card(
            elevation=2,
            content=ft.Container(
                padding=15,
                border_radius=8,
                on_click=lambda _: self.page.go(ruta),
                ink=True,
                content=ft.Column(
                    [
                        ft.Icon(icono, size=40, color=color_icono),
                        ft.Text(titulo, weight=ft.FontWeight.BOLD, size=16),
                        ft.Text(descripcion, size=12, color=ft.colors.OUTLINE, max_lines=3, overflow=ft.TextOverflow.ELLIPSIS)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                )
            )
        )

    def _cargar_accesos_directos(self):
        self.accesos_directos_grid.controls.clear()

        accesos = [
            {"titulo": "Gestionar Empresas", "icono": ft.icons.STOREFRONT_ROUNDED, "ruta": ROUTE_ADMIN_EMPRESAS, "desc": "Administra prestadores de servicios turísticos.", "color": ft.colors.TEAL_500},
            {"titulo": "Gestionar Atractivos", "icono": ft.icons.BEACH_ACCESS_ROUNDED, "ruta": ROUTE_ADMIN_ATRACTIVOS, "desc": "Inventario de atractivos turísticos.", "color": ft.colors.CYAN_600},
            {"titulo": "Gestionar Vacantes", "icono": ft.icons.WORK_HISTORY_ROUNDED, "ruta": ROUTE_ADMIN_VACANTES, "desc": "Publica y administra ofertas de empleo.", "color": ft.colors.AMBER_700},
            # Añadir más accesos según el rol
        ]

        # Lógica de permisos (muy básica)
        if self.user_rol == "SuperAdmin":
            accesos.append({"titulo": "Gestionar Usuarios", "icono": ft.icons.PEOPLE_ALT_ROUNDED, "ruta": ROUTE_ADMIN_USUARIOS, "desc": "Administra los usuarios del sistema.", "color": ft.colors.RED_500})
            accesos.append({"titulo": "Reportes Nacionales", "icono": ft.icons.LEADERBOARD_ROUNDED, "ruta": ROUTE_ADMIN_REPORTES_NACIONAL, "desc": "Visualiza datos a nivel nacional.", "color": ft.colors.PURPLE_500})

        for acceso in accesos:
            self.accesos_directos_grid.controls.append(
                self._crear_acceso_directo_card(acceso["titulo"], acceso["icono"], acceso["ruta"], acceso["desc"], acceso["color"])
            )
        self.update()

    def build(self):
        return ft.Column(
            [
                ft.Text(f"Bienvenido al Panel de Administración, {self.user_nombre_completo}", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("Resumen del Sistema", style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.W_300),
                self.kpi_cards_row,
                ft.Divider(height=20),
                ft.Text("Módulos de Gestión", style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.W_300),
                ft.Container(
                    content=self.accesos_directos_grid,
                    # expand=True # GridView necesita una altura definida o un padre con altura
                )
            ],
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=15,
            padding=ft.padding.symmetric(horizontal=25, vertical=15)
        )
