import flet as ft
from turismo_app.database import db_manager

class AdminEmpresasView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id_actual_edicion = None
        self.empresas_data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Razón Social")),
                ft.DataColumn(ft.Text("Municipio")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        # --- Controles del Formulario ---
        self.txt_razon_social_emp = ft.TextField(label="Razón Social / Nombre Comercial*", dense=True)
        self.txt_nit_emp = ft.TextField(label="NIT", dense=True)
        self.dd_tipo_prestador = ft.Dropdown(label="Tipo de Prestador Principal*", options=[], dense=True)
        self.chk_es_formal = ft.Checkbox(label="¿Es una empresa formalizada?")
        self.txt_rnt_emp = ft.TextField(label="Registro Nacional de Turismo (RNT)", dense=True)
        self.txt_descripcion_servicios = ft.TextField(label="Descripción de Servicios", multiline=True, min_lines=3, dense=True)
        self.txt_direccion_principal = ft.TextField(label="Dirección Principal", dense=True)
        self.txt_telefonos_contacto = ft.TextField(label="Teléfonos de Contacto", dense=True)
        self.txt_email_contacto = ft.TextField(label="Email de Contacto", dense=True)
        self.txt_pagina_web = ft.TextField(label="Página Web", dense=True)
        self.chk_aprobada_publicar = ft.Checkbox(label="¿Aprobada para ser pública?")
        self.dd_departamento = ft.Dropdown(label="Departamento*", on_change=self._on_departamento_change, dense=True)
        self.dd_municipio = ft.Dropdown(label="Municipio*", dense=True)
        self.category_dropdowns_container = ft.Column(spacing=10)
        self.btn_guardar_emp = ft.ElevatedButton(text="Guardar", on_click=self._guardar_empresa_handler)
        self.btn_cancelar_edicion = ft.ElevatedButton(text="Cancelar", on_click=self._cancelar_edicion_handler)
        self.dialogo_formulario = self._crear_dialogo_formulario()

        self._cargar_datos_iniciales()

    def _cargar_datos_iniciales(self):
        # Cargar departamentos
        deptos = db_manager.get_all_departamentos()
        self.dd_departamento.options = [ft.dropdown.Option(d['codigo_departamento'], d['nombre_departamento']) for d in deptos]
        # Cargar tipos de prestador
        self.dd_tipo_prestador.options = [
            ft.dropdown.Option("AGENCIA_VIAJES", "Agencia de Viajes"),
            ft.dropdown.Option("ALOJAMIENTO_URBANO", "Alojamiento Urbano"),
            ft.dropdown.Option("ALOJAMIENTO_RURAL", "Alojamiento Rural"),
            ft.dropdown.Option("RESTAURANTE_BAR", "Restaurante / Bar"),
            ft.dropdown.Option("OTRO", "Otro"),
        ]

    def _crear_dialogo_formulario(self):
        return ft.AlertDialog(
            modal=True, title=ft.Text("Registrar/Editar Empresa"),
            content=ft.Column(width=600, controls=[
                self.txt_razon_social_emp, self.txt_nit_emp, self.dd_tipo_prestador,
                self.chk_es_formal, self.txt_rnt_emp, self.txt_descripcion_servicios,
                self.txt_direccion_principal, self.txt_telefonos_contacto, self.txt_email_contacto,
                self.txt_pagina_web, self.chk_aprobada_publicar,
                ft.Row([self.dd_departamento, self.dd_municipio], spacing=10),
                ft.Text("Categorías Adicionales", weight=ft.FontWeight.BOLD),
                self.category_dropdowns_container
            ], scroll=ft.ScrollMode.ADAPTIVE),
            actions=[self.btn_guardar_emp, self.btn_cancelar_edicion],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _on_departamento_change(self, e):
        munis = db_manager.get_municipios_by_departamento(e.control.value)
        self.dd_municipio.options = [ft.dropdown.Option(m['codigo_municipio'], m['nombre_municipio']) for m in munis]
        self.dd_municipio.value = None
        self.page.update()

    def _guardar_empresa_handler(self, e):
        selected_categories = [int(dropdown.value) for dropdown in self.category_dropdowns_container.controls if dropdown.value]
        datos = {
            "razon_social_o_nombre_comercial": self.txt_razon_social_emp.value,
            "nit": self.txt_nit_emp.value,
            "tipo_prestador": self.dd_tipo_prestador.value,
            "es_formal": self.chk_es_formal.value, "rnt": self.txt_rnt_emp.value,
            "descripcion_servicios": self.txt_descripcion_servicios.value,
            "direccion_principal": self.txt_direccion_principal.value,
            "telefonos_contacto": self.txt_telefonos_contacto.value,
            "email_contacto": self.txt_email_contacto.value,
            "pagina_web": self.txt_pagina_web.value,
            "aprobada_publicar": self.chk_aprobada_publicar.value,
            "codigo_municipio": self.dd_municipio.value,
            "registrada_por_usuario_id": self.page.session.get("user_id"),
            "audit_user_id": self.page.session.get("user_id")
        }
        empresa_id = db_manager.crear_o_actualizar_empresa(datos, self.empresa_id_actual_edicion)
        if empresa_id:
            db_manager.update_empresa_categorias(empresa_id, selected_categories, self.page.session.get("user_id"))
        self.dialogo_formulario.open = False
        self._cargar_empresas()
        self.page.update()

    def _cargar_empresa_para_edicion(self, e):
        empresa = e.control.data
        self.empresa_id_actual_edicion = empresa.get("id_empresa")
        self.txt_razon_social_emp.value = empresa.get("razon_social_o_nombre_comercial")
        self.txt_nit_emp.value = empresa.get("nit")
        self.dd_tipo_prestador.value = empresa.get("tipo_prestador")
        self.dd_departamento.value = empresa.get("codigo_municipio")[:2]
        self._on_departamento_change(ft.ControlEvent("change", self.dd_departamento, self.dd_departamento.value))
        self.dd_municipio.value = empresa.get("codigo_municipio")

        self.category_dropdowns_container.controls.clear()
        empresa_categorias = db_manager.get_empresa_categorias(self.empresa_id_actual_edicion)
        if empresa_categorias:
            # NOTE: This logic assumes a company belongs to a single category branch,
            # as reflected by the linear dropdown UI. The last saved category is
            # assumed to be the leaf of the branch.
            leaf_category_id = empresa_categorias[-1]['id_categoria']
            path = db_manager.get_category_path(leaf_category_id)
            parent_id = None
            for category_in_path in path:
                dropdown = self._crear_dropdown_categoria(parent_id, selected_id=str(category_in_path['id_categoria']))
                if dropdown:
                    self.category_dropdowns_container.controls.append(dropdown)
                    parent_id = category_in_path['id_categoria']
            final_dropdown = self._crear_dropdown_categoria(parent_id)
            if final_dropdown:
                self.category_dropdowns_container.controls.append(final_dropdown)
        else:
            initial_dropdown = self._crear_dropdown_categoria(parent_id=None)
            if initial_dropdown:
                self.category_dropdowns_container.controls.append(initial_dropdown)
        self.dialogo_formulario.open = True
        self.page.update()

    def _crear_dropdown_categoria(self, parent_id, selected_id=None):
        options = [ft.dropdown.Option(str(cat['id_categoria']), cat['nombre_categoria']) for cat in db_manager.get_categorias_by_parent_id(parent_id)]
        if not options: return None
        return ft.Dropdown(label="Sub-Categoría", options=options, value=selected_id, on_change=self._on_category_change)

    def _on_category_change(self, e):
        selected_id = int(e.control.value)
        current_index = self.category_dropdowns_container.controls.index(e.control)
        self.category_dropdowns_container.controls = self.category_dropdowns_container.controls[:current_index + 1]
        new_dropdown = self._crear_dropdown_categoria(selected_id)
        if new_dropdown:
            self.category_dropdowns_container.controls.append(new_dropdown)
        self.dialogo_formulario.content.update()

    def _abrir_formulario_nueva_empresa(self, e):
        self.empresa_id_actual_edicion = None
        self.txt_razon_social_emp.value = ""
        self.dd_departamento.value = None
        self.dd_municipio.options = []
        self.dd_municipio.value = None
        self.category_dropdowns_container.controls.clear()
        initial_dropdown = self._crear_dropdown_categoria(parent_id=None)
        if initial_dropdown:
            self.category_dropdowns_container.controls.append(initial_dropdown)
        self.dialogo_formulario.open = True
        self.page.update()

    def _cancelar_edicion_handler(self, e):
        self.dialogo_formulario.open = False
        self.page.update()

    def _cargar_empresas(self):
        self.empresas_data_table.rows.clear()
        empresas, total = db_manager.listar_empresas_paginado_admin({}, {}, 100, 0)
        for empresa in empresas:
            self.empresas_data_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(empresa["razon_social_o_nombre_comercial"])),
                    ft.DataCell(ft.Text(empresa["nombre_municipio"])),
                    ft.DataCell(ft.Checkbox(value=empresa["activo"], disabled=True)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=self._cargar_empresa_para_edicion, data=empresa),
                        ft.IconButton(ft.icons.DELETE, on_click=self._eliminar_empresa_handler, data=empresa["id_empresa"]),
                    ])),
                ])
            )
        self.page.update()

    def _eliminar_empresa_handler(self, e):
        # Lógica de eliminación
        pass

    def build(self):
        self._cargar_empresas()
        return ft.Column(controls=[
            self.dialogo_formulario,
            ft.Text("Gestión de Empresas", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.ElevatedButton("Añadir Nueva Empresa", on_click=self._abrir_formulario_nueva_empresa),
            ft.Row(controls=[self.empresas_data_table], scroll=ft.ScrollMode.ALWAYS)
        ])
