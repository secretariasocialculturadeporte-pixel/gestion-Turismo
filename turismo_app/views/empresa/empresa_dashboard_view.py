import flet as ft
from turismo_app.database import db_manager

class EmpresaDashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_nombre = page.session.get("user_nombre_completo")
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.empresa_info = db_manager.obtener_empresa_por_id(self.empresa_id)
        self.nombre_empresa = self.empresa_info.get("razon_social_o_nombre_comercial") if self.empresa_info else "Empresa no encontrada"
        self.resumen_clientes = db_manager.obtener_resumen_clientes_por_empresa(self.empresa_id)

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
        # Crear la tabla de resumen de clientes
        tabla_resumen = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("País de Origen")),
                ft.DataColumn(ft.Text("Total Clientes"), numeric=True),
            ],
            rows=[
                ft.DataRow(cells=[ft.DataCell(ft.Text(row["pais_origen_cliente"])), ft.DataCell(ft.Text(str(row["total_clientes"])))])
                for row in self.resumen_clientes
            ]
        )

        return ft.Column(
            spacing=20,
            padding=30,
            controls=[
                ft.Text(f"Bienvenido, {self.user_nombre}", style=ft.TextThemeStyle.HEADLINE_LARGE),
                ft.Text(f"Panel de Gestión para: {self.nombre_empresa}", style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.colors.OUTLINE),
                ft.Divider(),
                ft.Text("Resumen de Clientes", style=ft.TextThemeStyle.TITLE_LARGE),
                tabla_resumen,
                ft.Divider(),
                ft.Text("Accesos Directos", style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Row(
                    controls=[
                        self._crear_acceso_directo(
                            "Gestionar Productos/Eventos",
                            ft.icons.CATEGORY,
                            "/empresa/productos"
                        ),
                        self._crear_acceso_directo(
                            "Registrar Clientes",
                            ft.icons.PEOPLE_ALT,
                            "/empresa/clientes"
                        ),
                        self._crear_acceso_directo(
                            "Editar Información de la Empresa",
                            ft.icons.EDIT_SQUARE,
                            f"/admin/empresas?edit_id={self.empresa_id}"
                        ),
                        self._crear_acceso_directo(
                            "Gestionar Inventario",
                            ft.icons.INVENTORY,
                            "/empresa/inventario"
                        ),
                        self._crear_acceso_directo(
                            "Calendario de Reservas",
                            ft.icons.CALENDAR_VIEW_MONTH,
                            "/empresa/calendario"
                        ),
                        self._crear_acceso_directo(
                            "Gestionar Recursos",
                            ft.icons.SETTINGS,
                            "/empresa/recursos"
                        ),
                        self._crear_acceso_directo(
                            "Reglas de Precios",
                            ft.icons.PRICE_CHANGE,
                            "/empresa/precios"
                        ),
                    ] + self._crear_accesos_directos_hotel(),
                    wrap=True,
                    spacing=20,
                    run_spacing=20
                )
            ]
        )

    def _crear_accesos_directos_hotel(self):
        if self.empresa_info and self.empresa_info.get("tipo_prestador") in ["ALOJAMIENTO_URBANO", "ALOJAMIENTO_RURAL"]:
            return [
                self._crear_acceso_directo(
                    "Configurar Habitaciones",
                    ft.icons.BED,
                    "/empresa/hotel/habitaciones"
                ),
                self._crear_acceso_directo(
                    "Gestionar Reservas",
                    ft.icons.BOOK,
                    "/empresa/hotel/reservas"
                ),
                self._crear_acceso_directo(
                    "Ver Calendario",
                    ft.icons.CALENDAR_MONTH,
                    "/empresa/hotel/calendario"
                ),
            ]

        if self.empresa_info and self.empresa_info.get("tipo_prestador") == "RESTAURANTE_BAR":
            return [
                self._crear_acceso_directo(
                    "Panel de Restaurante",
                    ft.icons.RESTAURANT_MENU,
                    "/empresa/restaurante/admin"
                )
            ]

        if self.empresa_info and self.empresa_info.get("tipo_prestador") == "AGENCIA_VIAJES":
            return [
                self._crear_acceso_directo(
                    "Gestionar Paquetes",
                    ft.icons.CARD_TRAVEL,
                    "/empresa/agencia/paquetes"
                ),
                self._crear_acceso_directo(
                    "Gestionar Reservas",
                    ft.icons.BOOK_ONLINE,
                    "/empresa/agencia/reservas"
                ),
            ]
        return []
