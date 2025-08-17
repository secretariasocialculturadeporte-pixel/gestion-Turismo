import flet as ft
from turismo_app.database import db_manager

class RestauranteGestionMesasView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.mesa_id_actual = None

        # Controles del formulario
        self.txt_nombre_mesa = ft.TextField(label="Nombre o Número de Mesa*")
        self.txt_capacidad = ft.TextField(label="Capacidad (personas)*", keyboard_type=ft.KeyboardType.NUMBER)
        self.btn_guardar = ft.ElevatedButton("Guardar Mesa", on_click=self._guardar_handler)

        # Tabla de mesas
        self.tabla_mesas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Capacidad")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_handler(self, e):
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_mesa": self.txt_nombre_mesa.value,
            "capacidad": int(self.txt_capacidad.value),
            "estado": "Libre", # Estado inicial
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_mesa(datos, self.mesa_id_actual)
        self._cargar_mesas()

    def _cargar_mesas(self):
        mesas = db_manager.listar_mesas_por_empresa(self.empresa_id)
        self.tabla_mesas.rows.clear()
        for mesa in mesas:
            self.tabla_mesas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(mesa["nombre_mesa"])),
                        ft.DataCell(ft.Text(str(mesa["capacidad"]))),
                        ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, data=mesa, on_click=self._editar_handler)),
                    ]
                )
            )
        self.page.update()

    def _editar_handler(self, e):
        mesa = e.control.data
        self.mesa_id_actual = mesa["id_mesa"]
        self.txt_nombre_mesa.value = mesa["nombre_mesa"]
        self.txt_capacidad.value = str(mesa["capacidad"])
        self.btn_guardar.text = "Actualizar"
        self.page.update()

    def build(self):
        self._cargar_mesas()
        formulario = ft.Column([
            self.txt_nombre_mesa,
            self.txt_capacidad,
            self.btn_guardar,
        ])

        return ft.Column(
            [
                ft.Text("Configuración de Mesas", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nueva/Editar Mesa", content=formulario),
                        ft.Tab(text="Listado de Mesas", content=ft.Column([self.tabla_mesas])),
                    ]
                )
            ]
        )
