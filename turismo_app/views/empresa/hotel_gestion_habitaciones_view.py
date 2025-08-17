import flet as ft
from turismo_app.database import db_manager

class HotelGestionHabitacionesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.habitacion_id_actual = None

        # Controles del formulario
        self.txt_nombre = ft.TextField(label="Nombre de la Habitación*")
        self.dd_tipo = ft.Dropdown(
            label="Tipo de Habitación*",
            options=[
                ft.dropdown.Option("Sencilla"),
                ft.dropdown.Option("Doble"),
                ft.dropdown.Option("Suite"),
                ft.dropdown.Option("Familiar"),
            ]
        )
        self.txt_capacidad = ft.TextField(label="Capacidad (personas)*", keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_precio = ft.TextField(label="Precio por Noche (COP)*", keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_descripcion = ft.TextField(label="Descripción", multiline=True)
        self.sw_activa = ft.Switch(label="Activa", value=True)
        self.btn_guardar = ft.ElevatedButton("Guardar", on_click=self._guardar_handler)
        self.btn_limpiar = ft.OutlinedButton("Limpiar", on_click=self._limpiar_formulario)

        # Tabla de habitaciones existentes
        self.tabla_habitaciones = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Capacidad")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Activa")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_handler(self, e):
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_habitacion": self.txt_nombre.value,
            "tipo_habitacion": self.dd_tipo.value,
            "capacidad": int(self.txt_capacidad.value),
            "precio_base": float(self.txt_precio.value),
            "descripcion": self.txt_descripcion.value,
            "activa": self.sw_activa.value,
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_habitacion(datos, self.habitacion_id_actual)
        self._limpiar_formulario()
        self._cargar_habitaciones()

    def _limpiar_formulario(self, e=None):
        self.habitacion_id_actual = None
        self.txt_nombre.value = ""
        self.dd_tipo.value = None
        self.txt_capacidad.value = ""
        self.txt_precio.value = ""
        self.txt_descripcion.value = ""
        self.sw_activa.value = True
        self.btn_guardar.text = "Guardar"
        self.page.update()

    def _cargar_habitaciones(self):
        habitaciones = db_manager.listar_habitaciones_por_empresa(self.empresa_id)
        self.tabla_habitaciones.rows.clear()
        for hab in habitaciones:
            self.tabla_habitaciones.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(hab["nombre_habitacion"])),
                        ft.DataCell(ft.Text(hab["tipo_habitacion"])),
                        ft.DataCell(ft.Text(str(hab["capacidad"]))),
                        ft.DataCell(ft.Text(f"{hab['precio_base']:.2f}")),
                        ft.DataCell(ft.Switch(value=bool(hab["activa"]), disabled=True)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, on_click=self._editar_handler, data=hab),
                            ft.IconButton(icon=ft.icons.DELETE, on_click=self._borrar_handler, data=hab["id_habitacion"]),
                        ])),
                    ]
                )
            )
        self.page.update()

    def _editar_handler(self, e):
        hab = e.control.data
        self.habitacion_id_actual = hab["id_habitacion"]
        self.txt_nombre.value = hab["nombre_habitacion"]
        self.dd_tipo.value = hab["tipo_habitacion"]
        self.txt_capacidad.value = str(hab["capacidad"])
        self.txt_precio.value = str(hab["precio_base"])
        self.txt_descripcion.value = hab["descripcion"]
        self.sw_activa.value = bool(hab["activa"])
        self.btn_guardar.text = "Actualizar"
        self.page.update()

    def _borrar_handler(self, e):
        # En una app real, aquí iría un diálogo de confirmación
        db_manager.borrar_habitacion(e.control.data) # Asume que esta función existe
        self._cargar_habitaciones()

    def build(self):
        self._cargar_habitaciones()
        formulario = ft.Container(
            ft.Column([
                self.txt_nombre,
                self.dd_tipo,
                self.txt_capacidad,
                self.txt_precio,
                self.txt_descripcion,
                self.sw_activa,
                ft.Row([self.btn_guardar, self.btn_limpiar])
            ]),
            padding=15
        )

        return ft.Column(
            [
                ft.Text("Configuración de Habitaciones", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(text="Nueva/Editar Habitación", content=formulario),
                        ft.Tab(text="Listado de Habitaciones", content=ft.Column([self.tabla_habitaciones])),
                    ]
                )
            ]
        )
