import flet as ft
from turismo_app.database import db_manager

class GestionCostosView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")

        # Controles del formulario
        self.txt_nombre_costo = ft.TextField(label="Nombre del Costo*")
        self.dd_tipo_costo = ft.Dropdown(
            label="Tipo de Costo*",
            options=[
                ft.dropdown.Option("Mano de Obra Directa"),
                ft.dropdown.Option("Materiales Directos"),
                ft.dropdown.Option("CIF"),
                ft.dropdown.Option("Administrativo"),
                ft.dropdown.Option("Ventas"),
            ]
        )
        self.sw_es_variable = ft.Switch(label="Es Variable", value=True)
        self.txt_unidad_medida = ft.TextField(label="Unidad de Medida", hint_text="Ej: Por Hora, Por Tour, Por Persona")
        self.txt_valor_costo = ft.TextField(label="Valor del Costo (COP)*", keyboard_type=ft.KeyboardType.NUMBER)
        self.btn_guardar = ft.ElevatedButton("Guardar Costo", on_click=self._guardar_handler)

        # Tabla de costos
        self.tabla_costos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Valor")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_handler(self, e):
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_costo": self.txt_nombre_costo.value,
            "tipo_costo": self.dd_tipo_costo.value,
            "es_variable": self.sw_es_variable.value,
            "unidad_medida": self.txt_unidad_medida.value,
            "valor_costo": float(self.txt_valor_costo.value),
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_costo(datos) # Asume que esta función existe
        self._cargar_costos()

    def _cargar_costos(self):
        costos = db_manager.listar_costos_por_empresa(self.empresa_id) # Asume que esta función existe
        self.tabla_costos.rows.clear()
        for costo in costos:
            self.tabla_costos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(costo["nombre_costo"])),
                        ft.DataCell(ft.Text(costo["tipo_costo"])),
                        ft.DataCell(ft.Text(f"{costo['valor_costo']:.2f}")),
                        ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, data=costo, on_click=self._editar_handler)),
                    ]
                )
            )
        self.page.update()

    def _editar_handler(self, e):
        # Lógica para editar un costo
        pass

    def build(self):
        self._cargar_costos()

        formulario = ft.Column([
            self.txt_nombre_costo,
            self.dd_tipo_costo,
            self.sw_es_variable,
            self.txt_unidad_medida,
            self.txt_valor_costo,
            self.btn_guardar,
        ])

        return ft.Column(
            [
                ft.Text("Gestión de Costos Operativos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nuevo/Editar Costo", content=formulario),
                        ft.Tab(text="Listado de Costos", content=ft.Column([self.tabla_costos])),
                    ]
                )
            ]
        )
