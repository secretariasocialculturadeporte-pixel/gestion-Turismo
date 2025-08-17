import flet as ft
from turismo_app.database import db_manager
import datetime
import math

class AdminAtractivosView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")
        self.atractivo_id_actual_edicion = None
        self.current_page = 1
        self.items_per_page = 10

        # --- Controles ---
        self.txt_nombre_atractivo = ft.TextField(label="Nombre del Atractivo*", dense=True)
        self.dd_tipo_categoria_principal = ft.Dropdown(label="Categoría Principal*", options=[ft.dropdown.Option(val) for val in ["SITIOS_NATURALES", "PATRIMONIO_CULTURAL", "EVENTOS"]])
        self.txt_descripcion_breve = ft.TextField(label="Descripción Breve", multiline=True)
        self.sw_aprobado_publicar = ft.Switch(label="Aprobado para Publicar")
        self.sw_activo = ft.Switch(label="Activo", value=True)
        self.btn_guardar = ft.ElevatedButton("Guardar", on_click=self._guardar_handler)
        self.btn_limpiar = ft.TextButton("Limpiar", on_click=self._limpiar_formulario)
        self.txt_filtro_nombre = ft.TextField(label="Buscar...", on_submit=self._aplicar_filtros)
        self.btn_aplicar_filtros = ft.IconButton(icon=ft.icons.SEARCH, on_click=self._aplicar_filtros)
        self.tabla_atractivos = ft.DataTable(columns=[ft.DataColumn(ft.Text(col)) for col in ["Nombre", "Categoría", "Activo", "Acciones"]])
        self.paginacion_controls = ft.Row()

        self.did_mount()

        # --- UI Construction ---
        formulario = ft.Container(content=ft.Column([self.txt_nombre_atractivo, self.dd_tipo_categoria_principal, self.txt_descripcion_breve, self.sw_aprobado_publicar, self.sw_activo, ft.Row([self.btn_guardar, self.btn_limpiar])]))
        listado = ft.Column([ft.Row([self.txt_filtro_nombre, self.btn_aplicar_filtros]), self.tabla_atractivos, self.paginacion_controls])
        self.controls = [ft.Text("Gestión de Atractivos", style=ft.TextThemeStyle.HEADLINE_MEDIUM), ft.Tabs(tabs=[ft.Tab("Formulario", content=formulario), ft.Tab("Listado", content=listado)])]

    def did_mount(self):
        self._cargar_listado_atractivos()

    def _aplicar_filtros(self, e):
        self.current_page = 1
        self._cargar_listado_atractivos()

    def _cargar_listado_atractivos(self):
        offset = (self.current_page - 1) * self.items_per_page
        filtros = {"codigo_municipio": self.codigo_municipio_admin, "nombre_atractivo__icontains": self.txt_filtro_nombre.value}
        atractivos, total_items = db_manager.listar_atractivos_admin_paginado(filtros, {}, self.items_per_page, offset)
        self.tabla_atractivos.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(a.get("nombre_atractivo"))), ft.DataCell(ft.Text(a.get("tipo_categoria_principal"))), ft.DataCell(ft.Icon(ft.icons.CHECK if a.get("activo") else ft.icons.CLOSE)), ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, data=a, on_click=self._cargar_para_edicion))]) for a in atractivos]
        self._actualizar_paginacion(total_items)
        self.update()

    def _actualizar_paginacion(self, total_items):
        # ...
        pass

    def _cargar_para_edicion(self, e):
        # ...
        pass

    def _limpiar_formulario(self, e=None):
        # ...
        pass

    def _guardar_handler(self, e):
        if not self.txt_nombre_atractivo.value or not self.dd_tipo_categoria_principal.value:
            self.txt_nombre_atractivo.error_text = "Obligatorio"
            self.dd_tipo_categoria_principal.error_text = "Obligatorio"
            self.update()
            return
        # ... (resto de la lógica de guardado) ...
        self._cargar_listado_atractivos()
