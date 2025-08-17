import flet as ft
from turismo_app.database import db_manager
import datetime

class HotelGestionReservasView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.reserva_id_actual = None

        # Controles del formulario
        self.dd_habitacion = ft.Dropdown(label="Habitación*")
        self.txt_nombre_huesped = ft.TextField(label="Nombre del Huésped*")
        self.txt_email_huesped = ft.TextField(label="Email del Huésped")
        self.txt_telefono_huesped = ft.TextField(label="Teléfono del Huésped")

        self.dp_fecha_inicio = ft.DatePicker(on_change=self._on_fecha_inicio_seleccionada)
        self.txt_fecha_inicio = ft.TextField(label="Fecha de Check-in*", read_only=True)
        self.btn_abrir_dp_inicio = ft.IconButton(icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.page.open(self.dp_fecha_inicio))

        self.dp_fecha_fin = ft.DatePicker(on_change=self._on_fecha_fin_seleccionada)
        self.txt_fecha_fin = ft.TextField(label="Fecha de Check-out*", read_only=True)
        self.btn_abrir_dp_fin = ft.IconButton(icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.page.open(self.dp_fecha_fin))

        self.dd_estado = ft.Dropdown(
            label="Estado de la Reserva*",
            options=[
                ft.dropdown.Option("Confirmada"),
                ft.dropdown.Option("Cancelada"),
                ft.dropdown.Option("Check-In"),
                ft.dropdown.Option("Check-Out"),
            ]
        )
        self.txt_notas = ft.TextField(label="Notas", multiline=True)
        self.btn_guardar = ft.ElevatedButton("Guardar Reserva", on_click=self._guardar_handler)

        # Tabla de reservas
        self.tabla_reservas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Habitación")),
                ft.DataColumn(ft.Text("Huésped")),
                ft.DataColumn(ft.Text("Fechas")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _on_fecha_inicio_seleccionada(self, e):
        self.txt_fecha_inicio.value = self.dp_fecha_inicio.value.strftime("%Y-%m-%d")
        self.page.update()

    def _on_fecha_fin_seleccionada(self, e):
        self.txt_fecha_fin.value = self.dp_fecha_fin.value.strftime("%Y-%m-%d")
        self.page.update()

    def _guardar_handler(self, e):
        # Simplificación: Buscar o crear huésped por documento de identidad
        huesped_id = db_manager.crear_o_actualizar_huesped({
            "nombre_completo": self.txt_nombre_huesped.value,
            "email": self.txt_email_huesped.value,
            "telefono": self.txt_telefono_huesped.value,
            "documento_identidad": self.txt_documento_huesped.value # Campo nuevo
        })

        datos = {
            "id_habitacion": self.dd_habitacion.value,
            "id_huesped": huesped_id,
            "fecha_inicio": self.txt_fecha_inicio.value,
            "fecha_fin": self.txt_fecha_fin.value,
            "estado": self.dd_estado.value,
            "notas": self.txt_notas.value,
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_reserva(datos, self.reserva_id_actual)
        self._cargar_reservas()

    def _cargar_reservas(self):
        # Lógica para cargar todas las reservas de la empresa
        pass

    def build(self):
        # Cargar habitaciones en el dropdown
        habitaciones = db_manager.listar_habitaciones_por_empresa(self.empresa_id)
        self.dd_habitacion.options = [ft.dropdown.Option(h["id_habitacion"], h["nombre_habitacion"]) for h in habitaciones]

        self.txt_documento_huesped = ft.TextField(label="Documento del Huésped*") # Añadir este campo

        formulario = ft.Column([
            self.dd_habitacion,
            self.txt_nombre_huesped,
            self.txt_documento_huesped,
            self.txt_email_huesped,
            self.txt_telefono_huesped,
            ft.Row([self.txt_fecha_inicio, self.btn_abrir_dp_inicio]),
            ft.Row([self.txt_fecha_fin, self.btn_abrir_dp_fin]),
            self.dd_estado,
            self.txt_notas,
            self.btn_guardar,
        ])

        return ft.Column(
            [
                ft.Text("Gestión de Reservas", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nueva/Editar Reserva", content=formulario),
                        ft.Tab(text="Listado de Reservas", content=ft.Column([self.tabla_reservas])),
                    ]
                )
            ]
        )
