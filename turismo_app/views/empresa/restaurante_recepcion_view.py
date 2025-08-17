import flet as ft
from turismo_app.database import db_manager

class RestauranteRecepcionView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")

        # Controles
        self.txt_nombre_cliente = ft.TextField(label="Nombre del Cliente*")
        self.txt_num_personas = ft.TextField(label="Número de Personas*", keyboard_type=ft.KeyboardType.NUMBER)
        self.dp_fecha_reserva = ft.DatePicker()
        self.btn_fecha_reserva = ft.OutlinedButton("Fecha de Reserva", on_click=lambda _: self.page.open(self.dp_fecha_reserva))
        self.btn_guardar_reserva = ft.ElevatedButton("Guardar Reserva", on_click=self._guardar_reserva_handler)

        self.tabla_reservas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Personas")),
                ft.DataColumn(ft.Text("Fecha y Hora")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_reserva_handler(self, e):
        # Lógica de guardado de reserva de mesa
        pass

    def build(self):
        formulario = ft.Column([
            self.txt_nombre_cliente,
            self.txt_num_personas,
            self.btn_fecha_reserva,
            self.btn_guardar_reserva,
        ])

        return ft.Column(
            [
                ft.Text("Gestión de Reservas de Mesas", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nueva Reserva", content=formulario),
                        ft.Tab(text="Listado de Reservas", content=ft.Column([self.tabla_reservas])),
                    ]
                )
            ]
        )
