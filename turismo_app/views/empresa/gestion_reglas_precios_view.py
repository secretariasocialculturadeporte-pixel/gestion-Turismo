import flet as ft
from turismo_app.database import db_manager

class GestionReglasPreciosView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")

        # Controles del formulario
        self.txt_nombre_regla = ft.TextField(label="Nombre de la Regla*")
        self.dd_tipo_regla = ft.Dropdown(
            label="Tipo de Regla*",
            options=[
                ft.dropdown.Option("temporada"),
                ft.dropdown.Option("dia_semana"),
                ft.dropdown.Option("demanda"),
            ]
        )
        self.txt_valor_ajuste = ft.TextField(label="Valor de Ajuste*", hint_text="Ej: 1.2 para +20%, 0.8 para -20%", keyboard_type=ft.KeyboardType.NUMBER)
        self.dp_fecha_inicio = ft.DatePicker()
        self.btn_fecha_inicio = ft.OutlinedButton("Fecha de Inicio", on_click=lambda _: self.page.open(self.dp_fecha_inicio))
        self.dp_fecha_fin = ft.DatePicker()
        self.btn_fecha_fin = ft.OutlinedButton("Fecha de Fin", on_click=lambda _: self.page.open(self.dp_fecha_fin))
        self.txt_dias_semana = ft.TextField(label="Días de la Semana (1-7)", hint_text="Ej: 6,7 para Sáb, Dom")
        self.btn_guardar = ft.ElevatedButton("Guardar Regla", on_click=self._guardar_handler)

        # Tabla de reglas
        self.tabla_reglas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Ajuste")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_handler(self, e):
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_regla": self.txt_nombre_regla.value,
            "tipo_regla": self.dd_tipo_regla.value,
            "valor_ajuste": float(self.txt_valor_ajuste.value),
            "fecha_inicio": self.dp_fecha_inicio.value.strftime("%Y-%m-%d") if self.dp_fecha_inicio.value else None,
            "fecha_fin": self.dp_fecha_fin.value.strftime("%Y-%m-%d") if self.dp_fecha_fin.value else None,
            "dias_semana": self.txt_dias_semana.value,
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_regla_precio(datos)
        self._cargar_reglas()

    def _cargar_reglas(self):
        reglas = db_manager.listar_reglas_precios_por_empresa(self.empresa_id)
        self.tabla_reglas.rows.clear()
        for regla in reglas:
            self.tabla_reglas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(regla["nombre_regla"])),
                        ft.DataCell(ft.Text(regla["tipo_regla"])),
                        ft.DataCell(ft.Text(str(regla["valor_ajuste"]))),
                        ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, data=regla, on_click=self._editar_handler)),
                    ]
                )
            )
        self.page.update()

    def _editar_handler(self, e):
        # Lógica para editar una regla
        pass

    def build(self):
        self._cargar_reglas()

        formulario = ft.Column([
            self.txt_nombre_regla,
            self.dd_tipo_regla,
            self.txt_valor_ajuste,
            self.btn_fecha_inicio,
            self.btn_fecha_fin,
            self.txt_dias_semana,
            self.btn_guardar,
        ])

        return ft.Column(
            [
                ft.Text("Gestión de Reglas de Precios Dinámicos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nueva/Editar Regla", content=formulario),
                        ft.Tab(text="Listado de Reglas", content=ft.Column([self.tabla_reglas])),
                    ]
                )
            ]
        )
