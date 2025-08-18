import flet as ft
from turismo_app.database import db_manager

class GestionRecursosView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.recurso_id_actual = None

        # Controles del formulario
        self.txt_nombre_recurso = ft.TextField(label="Nombre del Recurso*")
        self.dd_tipo_recurso = ft.Dropdown(label="Tipo de Recurso*")
        self.txt_capacidad = ft.TextField(label="Capacidad*", keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_precio = ft.TextField(label="Precio Base*", keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_descripcion = ft.TextField(label="Descripción", multiline=True)
        self.sw_activo = ft.Switch(label="Activo", value=True)
        self.btn_guardar = ft.ElevatedButton("Guardar Recurso", on_click=self._guardar_handler)

        # Tabla de recursos
        self.tabla_recursos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Capacidad")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_handler(self, e):
        # Lógica de guardado
        pass

    def build(self):
        formulario = ft.Column([
            self.txt_nombre_recurso,
            self.dd_tipo_recurso,
            self.txt_capacidad,
            self.txt_precio,
            self.txt_descripcion,
            self.sw_activo,
            self.btn_guardar,
        ])

        return ft.Column(
            [
                ft.Text("Gestión de Recursos Reservables", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nuevo/Editar Recurso", content=formulario),
                        ft.Tab(text="Listado de Recursos", content=ft.Column([self.tabla_recursos])),
                    ]
                )
            ]
        )
