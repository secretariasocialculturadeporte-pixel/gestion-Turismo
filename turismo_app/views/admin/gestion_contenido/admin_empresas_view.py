import flet as ft
from turismo_app.database import db_manager
import datetime
import re
import math
import time

class AdminEmpresasView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_actual_gestion = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")
        self.rol_admin = page.session.get("user_rol")
        self.empresa_id_actual_edicion = None

        # Paginación y filtros
        self.filtros_listado_empresas = {}
        self.orden_listado_empresas = {"razon_social_o_nombre_comercial": "ASC"}
        self.current_page_empresas = 1
        self.items_per_page_empresas = 10
        self.total_items_empresas = 0

        # --- Selector de Municipio para SuperAdmins ---
        self.dd_municipio_gestion_sa_emp = ft.Dropdown(
            label="Gestionar Empresas del Municipio",
            visible=(self.rol_admin == "SuperAdmin"),
            on_change=self._on_municipio_gestion_sa_change,
            # Las opciones se cargarán en did_mount si es SuperAdmin
        )

        # === CAMPOS DEL FORMULARIO ===
        self.txt_razon_social_emp = ft.TextField(label="Razón Social / Nombre Comercial*", dense=True)
        self.txt_nit_emp = ft.TextField(label="NIT (sin dígito de verificación)", dense=True, hint_text="Ej: 900123456")
        self.dd_tipo_prestador_emp = ft.Dropdown(
            label="Tipo de Prestador*",
            options=[
                ft.dropdown.Option("", "--Seleccione--"),
                ft.dropdown.Option("ALOJAMIENTO_URBANO", "Aloj. Urbano"),
                ft.dropdown.Option("ALOJAMIENTO_RURAL", "Aloj. Rural"),
                ft.dropdown.Option("RESTAURANTE_BAR", "Restaurante/Bar"),
                ft.dropdown.Option("AGENCIA_VIAJES", "Agencia de Viajes"),
                ft.dropdown.Option("TRANSPORTE_TURISTICO", "Transporte Turístico"),
                ft.dropdown.Option("GUIA_TURISTICO", "Guía Turístico"),
                ft.dropdown.Option("OTRO_TIPO_EMPRESA", "Otro")
            ],
            dense=True,
            on_change=self._toggle_empresa_campos_cond_form
        )
        self.txt_tipo_prestador_otro_emp = ft.TextField(label="Especifique Otro Tipo Prestador", visible=False, dense=True)
        self.sw_es_formal_emp = ft.Switch(label="¿Formalizado? (RNT/Reg. Mercantil)", value=True, on_change=self._toggle_empresa_campos_cond_form)
        self.txt_rnt_emp = ft.TextField(label="No. RNT (Si aplica)", visible=True, dense=True)
        self.txt_descripcion_servicios_emp = ft.TextField(label="Descripción Servicios/Productos*", multiline=True, min_lines=3, dense=True)
        self.txt_direccion_principal_emp = ft.TextField(label="Dirección Principal*", dense=True)
        self.txt_telefonos_contacto_emp = ft.TextField(label="Teléfonos de Contacto*", hint_text="Separados por coma", dense=True)
        self.txt_email_contacto_emp = ft.TextField(label="Email de Contacto*", keyboard_type=ft.KeyboardType.EMAIL, dense=True)
        self.txt_pagina_web_emp = ft.TextField(label="Página Web / Red Social", keyboard_type=ft.KeyboardType.URL, dense=True)
        self.sw_aprobada_publicar_emp = ft.Switch(label="Aprobar para Directorio Público", value=False)
        self.sw_activo_emp = ft.Switch(label="Empresa/Prestador Activo", value=True)

        # Botones y Diálogo
        self.btn_guardar_emp = ft.ElevatedButton(text="Guardar Nueva Empresa", on_click=self._guardar_empresa_handler, icon=ft.icons.SAVE)
        self.btn_limpiar_emp = ft.TextButton(text="Limpiar Formulario", on_click=self._limpiar_formulario_empresa_completo, icon=ft.icons.CLEAR_ALL)

        # --- Filtros para Listado ---
        self.txt_filtro_nombre_emp = ft.TextField(label="Buscar por Nombre", dense=True, on_submit=self._aplicar_filtros_empresas)
        self.btn_aplicar_filtros = ft.IconButton(icon=ft.icons.SEARCH, on_click=self._aplicar_filtros_empresas, tooltip="Aplicar filtros")

        # --- Tabla de Listado y Paginación ---
        self.tabla_empresas_admin = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Razón Social")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Municipio")),
                ft.DataColumn(ft.Text("Aprobada"), on_sort=lambda e: self._cambiar_orden_y_recargar("aprobada_publicar", e.ascending)),
                ft.DataColumn(ft.Text("Activo"), on_sort=lambda e: self._cambiar_orden_y_recargar("activo", e.ascending)),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )
        self.loading_tabla_emp = ft.ProgressRing(visible=False)
        self.paginacion_emp_controls_container = ft.Row()

    def did_mount(self):
        if self.rol_admin == "SuperAdmin":
            # Cargar todos los municipios para el SuperAdmin
            # Esta es una simplificación. En una app real, podría necesitar paginación o búsqueda para municipios.
            all_municipios = []
            for depto in db_manager.obtener_departamentos():
                all_municipios.extend(db_manager.obtener_municipios_por_departamento(depto['codigo_departamento']))

            self.dd_municipio_gestion_sa_emp.options = [ft.dropdown.Option(m['codigo_municipio'], f"{m['nombre_municipio']} ({m['codigo_departamento']})") for m in all_municipios]

        self._cargar_listado_empresas()

    def _on_municipio_gestion_sa_change(self, e):
        self.codigo_municipio_actual_gestion = e.control.value
        self._cargar_listado_empresas()

    def _toggle_empresa_campos_cond_form(self, e=None):
        es_formal = self.sw_es_formal_emp.value
        self.txt_rnt_emp.visible = es_formal

        es_otro_tipo = self.dd_tipo_prestador_emp.value == "OTRO_TIPO_EMPRESA"
        self.txt_tipo_prestador_otro_emp.visible = es_otro_tipo
        self.update()

    def _validar_formulario_empresa(self) -> bool:
        valido = True
        if not self.txt_razon_social_emp.value:
            self.txt_razon_social_emp.error_text = "Obligatorio"; valido = False
        else: self.txt_razon_social_emp.error_text = None

        if not self.dd_tipo_prestador_emp.value:
            self.dd_tipo_prestador_emp.error_text = "Obligatorio"; valido = False
        else: self.dd_tipo_prestador_emp.error_text = None

        # ... más validaciones ...
        self.update()
        return valido

    def _recoger_datos_formulario_empresa(self) -> dict | None:
        if not self._validar_formulario_empresa():
            return None

        return {
            "razon_social_o_nombre_comercial": self.txt_razon_social_emp.value,
            "nit": self.txt_nit_emp.value,
            "tipo_prestador": self.dd_tipo_prestador_emp.value,
            "tipo_prestador_otro": self.txt_tipo_prestador_otro_emp.value if self.txt_tipo_prestador_otro_emp.visible else None,
            "es_formal": 1 if self.sw_es_formal_emp.value else 0,
            "rnt": self.txt_rnt_emp.value if self.sw_es_formal_emp.value else None,
            "descripcion_servicios": self.txt_descripcion_servicios_emp.value,
            "direccion_principal": self.txt_direccion_principal_emp.value,
            "telefonos_contacto": self.txt_telefonos_contacto_emp.value,
            "email_contacto": self.txt_email_contacto_emp.value,
            "pagina_web": self.txt_pagina_web_emp.value,
            "codigo_municipio": self.codigo_municipio_actual_gestion,
            "aprobada_publicar": 1 if self.sw_aprobada_publicar_emp.value else 0,
            "activo": 1 if self.sw_activo_emp.value else 0,
            "registrada_por_usuario_id": self.user_id_admin,
            "fecha_ultima_actualizacion": datetime.datetime.now().isoformat(),
        }

    def _limpiar_formulario_empresa_completo(self, e=None):
        self.empresa_id_actual_edicion = None
        self.txt_razon_social_emp.value = ""
        self.txt_nit_emp.value = ""
        self.dd_tipo_prestador_emp.value = None
        # ... limpiar todos los campos y errores ...
        self.btn_guardar_emp.text = "Guardar Nueva Empresa"
        self._toggle_empresa_campos_cond_form()
        self.update()

    def _cargar_empresa_para_edicion(self, e):
        empresa_id = e.control.data
        emp_data = db_manager.obtener_empresa_por_id(empresa_id)
        if emp_data:
            self._limpiar_formulario_empresa_completo()
            self.empresa_id_actual_edicion = empresa_id
            self.txt_razon_social_emp.value = emp_data.get("razon_social_o_nombre_comercial")
            self.txt_nit_emp.value = emp_data.get("nit")
            self.dd_tipo_prestador_emp.value = emp_data.get("tipo_prestador")
            # ... poblar todos los campos ...
            self.sw_aprobada_publicar_emp.value = emp_data.get("aprobada_publicar") == 1
            self.sw_activo_emp.value = emp_data.get("activo") == 1

            self.btn_guardar_emp.text = "Actualizar Empresa"
            self._toggle_empresa_campos_cond_form()
            # Debería cambiar a la pestaña del formulario
            self.page.tabs.selected_index = 0
            self.update()

    def _guardar_empresa_handler(self, e):
        if not self.codigo_municipio_actual_gestion:
            # Mostrar error: debe seleccionar un municipio
            return

        datos = self._recoger_datos_formulario_empresa()
        if datos:
            resultado_id = db_manager.crear_o_actualizar_empresa(datos, self.empresa_id_actual_edicion)
            if resultado_id:
                # Mostrar snackbar de éxito
                self._limpiar_formulario_empresa_completo()
                self._cargar_listado_empresas()
            else:
                # Mostrar snackbar de error
                pass

    def _aplicar_filtros_empresas(self, e):
        self.current_page_empresas = 1
        self._cargar_listado_empresas()

    def _cargar_listado_empresas(self):
        self.loading_tabla_emp.visible = True
        self.update()

        self.filtros_listado_empresas = {
            "razon_social__icontains": self.txt_filtro_nombre_emp.value or None,
            "codigo_municipio": self.codigo_municipio_actual_gestion,
        }
        self.filtros_listado_empresas = {k: v for k, v in self.filtros_listado_empresas.items() if v is not None}

        offset = (self.current_page_empresas - 1) * self.items_per_page_empresas

        resultados, total_items = db_manager.listar_empresas_paginado_admin(
            filtros=self.filtros_listado_empresas,
            orden=self.orden_listado_empresas,
            limit=self.items_per_page_empresas,
            offset=offset
        )
        self.total_items_empresas = total_items
        self.tabla_empresas_admin.rows.clear()

        for emp in resultados:
            self.tabla_empresas_admin.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(emp['razon_social_o_nombre_comercial'])),
                    ft.DataCell(ft.Text(emp['tipo_prestador'])),
                    ft.DataCell(ft.Text(emp['nombre_municipio'])),
                    ft.DataCell(ft.Icon(ft.icons.CHECK_CIRCLE if emp['aprobada_publicar'] else ft.icons.CANCEL_OUTLINED)),
                    ft.DataCell(ft.Icon(ft.icons.TOGGLE_ON if emp['activo'] else ft.icons.TOGGLE_OFF)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, data=emp['id'], on_click=self._cargar_empresa_para_edicion),
                        # ft.IconButton(ft.icons.DELETE_FOREVER, data=emp['id'], on_click=self._eliminar_empresa_handler),
                    ])),
                ]
            ))

        self.loading_tabla_emp.visible = False
        self._actualizar_controles_paginacion_empresas()
        self.update()

    def _actualizar_controles_paginacion_empresas(self):
        # Similar a la otra vista
        pass

    def _cambiar_orden_y_recargar(self, col, asc):
        pass

    def build(self):
        formulario = ft.Container(
            ft.Column([
                self.txt_razon_social_emp, self.txt_nit_emp, self.dd_tipo_prestador_emp, self.txt_tipo_prestador_otro_emp,
                self.sw_es_formal_emp, self.txt_rnt_emp, self.txt_descripcion_servicios_emp, self.txt_direccion_principal_emp,
                self.txt_telefonos_contacto_emp, self.txt_email_contacto_emp, self.txt_pagina_web_emp,
                ft.Divider(),
                self.sw_aprobada_publicar_emp, self.sw_activo_emp,
                ft.Row([self.btn_guardar_emp, self.btn_limpiar_emp], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=20
        )

        listado = ft.Container(
            ft.Column([
                ft.ResponsiveRow([
                    ft.Column([self.txt_filtro_nombre_emp], col={"sm":12, "md": 8}),
                    ft.Column([self.btn_aplicar_filtros], col={"sm":12, "md": 4}),
                ]),
                self.loading_tabla_emp,
                self.tabla_empresas_admin,
                self.paginacion_emp_controls_container
            ]),
            padding=20
        )

        return ft.Column([
            ft.Text("Gestión de Empresas y Prestadores Turísticos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            self.dd_municipio_gestion_sa_emp,
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Formulario de Empresa", icon=ft.icons.EDIT_DOCUMENT, content=formulario),
                    ft.Tab(text="Listado de Empresas", icon=ft.icons.LIST_ALT, content=listado),
                ],
                expand=True,
            )
        ])
