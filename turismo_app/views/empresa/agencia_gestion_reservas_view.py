import flet as ft
from turismo_app.database import db_manager

class AgenciaGestionReservasView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")

        # Controles
        self.dd_paquete = ft.Dropdown(label="Paquete Turístico*")
        self.txt_nombre_cliente = ft.TextField(label="Nombre del Cliente*")
        self.txt_num_personas = ft.TextField(label="Número de Personas*", keyboard_type=ft.KeyboardType.NUMBER)
        self.dp_fecha_inicio = ft.DatePicker()
        self.btn_fecha_inicio = ft.OutlinedButton("Fecha de Inicio", on_click=lambda _: self.page.open(self.dp_fecha_inicio))
        self.btn_guardar = ft.ElevatedButton("Guardar Reserva", on_click=self._guardar_handler)

        # Tabla de reservas
        self.tabla_reservas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Paquete")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Personas")),
                ft.DataColumn(ft.Text("Fecha Inicio")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_handler(self, e):
        # Simplificación: Asume que el cliente ya es un usuario del sistema
        # En una app real, aquí habría una búsqueda de clientes
        cliente_id = 1 # Placeholder

        datos = {
            "id_paquete": self.dd_paquete.value,
            "id_cliente": cliente_id,
            "fecha_inicio": self.dp_fecha_inicio.value.strftime("%Y-%m-%d"),
            "numero_personas": int(self.txt_num_personas.value),
            "estado": "Confirmada",
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_reserva_paquete(datos)
        self._cargar_reservas()

    def _cargar_reservas(self):
        reservas = db_manager.listar_reservas_paquetes_por_agencia(self.empresa_id)
        self.tabla_reservas.rows.clear()
        for r in reservas:
            self.tabla_reservas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r["nombre_paquete"])),
                        ft.DataCell(ft.Text(r["nombre_cliente"])),
                        ft.DataCell(ft.Text(str(r["numero_personas"]))),
                        ft.DataCell(ft.Text(r["fecha_inicio"])),
                        ft.DataCell(ft.Text(r["estado"])),
                        ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, data=r, on_click=self._editar_handler)),
                    ]
                )
            )
        self.page.update()

    def _editar_handler(self, e):
        # Lógica para editar una reserva
        pass

    def build(self):
        # Cargar paquetes en el dropdown
        paquetes = db_manager.listar_paquetes_por_agencia(self.empresa_id)
        self.dd_paquete.options = [ft.dropdown.Option(p["id_paquete"], p["nombre_paquete"]) for p in paquetes]

        self._cargar_reservas()

        formulario = ft.Column([
            self.dd_paquete,
            self.txt_nombre_cliente,
            self.txt_num_personas,
            self.btn_fecha_inicio,
            self.btn_guardar,
        ])

        return ft.Column(
            [
                ft.Text("Gestión de Reservas de Paquetes", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nueva Reserva", content=formulario),
                        ft.Tab(text="Listado de Reservas", content=ft.Column([self.tabla_reservas])),
                    ]
                )
            ]
        )
