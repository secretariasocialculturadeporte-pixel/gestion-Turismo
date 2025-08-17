import flet as ft
from turismo_app.database import db_manager
import datetime
import re
import math

class AdminEmpresasView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")
        self.rol_admin = page.session.get("user_rol")
        self.empresa_id_actual_edicion = None

        # Paginación y filtros
        self.filtros_listado_empresas = {}
        self.orden_listado_empresas = {"razon_social_o_nombre_comercial": "ASC"}
        self.current_page_empresas = 1
        self.items_per_page_empresas = 10

        # --- Controles del Formulario ---
        self.txt_razon_social_emp = ft.TextField(label="Razón Social / Nombre Comercial*", dense=True)
        self.txt_nit_emp = ft.TextField(label="NIT (sin dígito de verificación)", dense=True, hint_text="Ej: 900123456")
        self.dd_tipo_prestador_emp = ft.Dropdown(label="Tipo de Prestador*", options=[ft.dropdown.Option(value, text) for value, text in [("ALOJAMIENTO_URBANO", "Aloj. Urbano"), ("ALOJAMIENTO_RURAL", "Aloj. Rural"), ("RESTAURANTE_BAR", "Restaurante/Bar"), ("OTRO", "Otro")]], dense=True)
        self.txt_descripcion_servicios_emp = ft.TextField(label="Descripción Servicios/Productos*", multiline=True, min_lines=3, dense=True)
        self.txt_direccion_principal_emp = ft.TextField(label="Dirección Principal*", dense=True)
        self.txt_telefonos_contacto_emp = ft.TextField(label="Teléfonos de Contacto*", hint_text="Separados por coma", dense=True)
        self.txt_email_contacto_emp = ft.TextField(label="Email de Contacto*", keyboard_type=ft.KeyboardType.EMAIL, dense=True)

        self.btn_guardar_emp = ft.ElevatedButton(text="Guardar", on_click=self._guardar_empresa_handler)
        self.btn_limpiar_emp = ft.TextButton(text="Limpiar", on_click=self._limpiar_formulario_empresa_completo)

        # --- Controles del Listado ---
        self.txt_filtro_nombre_emp = ft.TextField(label="Buscar por Nombre", dense=True, on_submit=self._aplicar_filtros_empresas)
        self.btn_aplicar_filtros = ft.IconButton(icon=ft.icons.SEARCH, on_click=self._aplicar_filtros_empresas)
        self.tabla_empresas_admin = ft.DataTable(columns=[ft.DataColumn(ft.Text(col)) for col in ["Razón Social", "Tipo", "Municipio", "Acciones"]])

        self.did_mount()

        # --- Construcción de la UI ---
        formulario = ft.Container(content=ft.Column([self.txt_razon_social_emp, self.txt_nit_emp, self.dd_tipo_prestador_emp, self.txt_descripcion_servicios_emp, self.txt_direccion_principal_emp, self.txt_telefonos_contacto_emp, self.txt_email_contacto_emp, ft.Row([self.btn_guardar_emp, self.btn_limpiar_emp])]), padding=10)
        listado = ft.Column([ft.Row([self.txt_filtro_nombre_emp, self.btn_aplicar_filtros]), self.tabla_empresas_admin])
        self.controls = [ft.Text("Gestión de Empresas", style=ft.TextThemeStyle.HEADLINE_MEDIUM), ft.Tabs(tabs=[ft.Tab(text="Formulario", content=formulario), ft.Tab(text="Listado", content=listado)])]

    def did_mount(self):
        self._cargar_listado_empresas()

    def _aplicar_filtros_empresas(self, e):
        self.current_page_empresas = 1
        self._cargar_listado_empresas()

    def _cargar_listado_empresas(self):
        offset = (self.current_page_empresas - 1) * self.items_per_page_empresas
        filtros = {"codigo_municipio": self.codigo_municipio_admin, "razon_social__icontains": self.txt_filtro_nombre_emp.value or None}
        empresas, _ = db_manager.listar_empresas_paginado_admin(filtros, self.orden_listado_empresas, self.items_per_page_empresas, offset)
        self.tabla_empresas_admin.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(emp.get(field))) for field in ["razon_social_o_nombre_comercial", "tipo_prestador", "nombre_municipio"]] + [ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, on_click=self._cargar_empresa_para_edicion, data=emp))]) for emp in empresas]
        self.update()

    def _cargar_empresa_para_edicion(self, e):
        # ...
        pass

    def _guardar_empresa_handler(self, e):
        if not self._validar_formulario_empresa():
            return
        # ... (resto de la lógica de guardado) ...

    def _validar_formulario_empresa(self) -> bool:
        es_valido = True
        # Limpiar errores previos
        for control in [self.txt_razon_social_emp, self.txt_nit_emp, self.dd_tipo_prestador_emp, self.txt_email_contacto_emp]:
            control.error_text = None

        # Validación de Razón Social
        if not self.txt_razon_social_emp.value:
            self.txt_razon_social_emp.error_text = "La razón social es obligatoria."
            es_valido = False

        # Validación de NIT (simple, solo números)
        if self.txt_nit_emp.value and not re.match(r"^\d+$", self.txt_nit_emp.value):
            self.txt_nit_emp.error_text = "El NIT solo debe contener números."
            es_valido = False

        # Validación de Tipo de Prestador
        if not self.dd_tipo_prestador_emp.value:
            self.dd_tipo_prestador_emp.error_text = "Seleccione un tipo de prestador."
            es_valido = False

        # Validación de Email
        if self.txt_email_contacto_emp.value and not re.match(r"[^@]+@[^@]+\.[^@]+", self.txt_email_contacto_emp.value):
            self.txt_email_contacto_emp.error_text = "Formato de email inválido."
            es_valido = False

        self.update()
        return es_valido

    def _limpiar_formulario_empresa_completo(self, e=None):
        # ...
        pass
