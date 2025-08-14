import flet as ft
from turismo_app.database import db_manager
import math
import datetime

# Constantes para tipo de entidad en paginación y carga
TIPO_ATRACTIVO = "atractivos"
TIPO_EMPRESA = "empresas"

class CiudadanoTurismoView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.dialogo_detalle = ft.AlertDialog(modal=True, title=ft.Text("Detalle"))

        # Estado de la Paginación y Filtros (usando diccionarios para manejar ambos tipos)
        self.current_page = {TIPO_ATRACTIVO: 1, TIPO_EMPRESA: 1}
        self.items_per_page = 10
        self.total_items = {TIPO_ATRACTIVO: 0, TIPO_EMPRESA: 0}

        # Estado de selección y filtros
        self.departamentos_options = []
        self.municipios_options = []
        self.selected_departamento_codigo = None
        self.selected_municipio_codigo = page.session.get("user_codigo_municipio")
        self.filtros_aplicados_atractivos = {}
        self.filtros_aplicados_empresas = {}
        self.orden_actual_atractivos = {"a.nombre_atractivo": "ASC"}  # 'a' es el alias en db_manager
        self.orden_actual_empresas = {"e.razon_social_o_nombre_comercial": "ASC"} # 'e' es el alias

        # --- Selectores Globales de Ubicación ---
        self.dd_departamento_global = ft.Dropdown(label="Departamento", hint_text="Elija departamento", options=[], on_change=self._on_departamento_global_change, width=280, dense=True, content_padding=8)
        self.dd_municipio_global = ft.Dropdown(label="Municipio", hint_text="Elija municipio", options=[ft.dropdown.Option("", "--Seleccione Depto.--")], on_change=self._on_municipio_global_change, disabled=True, width=280, dense=True, content_padding=8)
        self.loading_selector_muni = ft.ProgressRing(width=16, height=16, visible=False, stroke_width=2)

        # --- Sección Atractivos ---
        self.txt_filtro_nombre_atractivo = ft.TextField(label="Buscar Atractivo por Nombre", dense=True, width=250, on_submit=lambda e: self._aplicar_filtros_y_cargar_listados_ciudadano(TIPO_ATRACTIVO))
        self.dd_filtro_tipo_categoria_atractivo = ft.Dropdown(label="Categoría Principal", options=[ft.dropdown.Option("", "Todas")], dense=True, width=220, on_change=lambda e: self._aplicar_filtros_y_cargar_listados_ciudadano(TIPO_ATRACTIVO))
        self.tabla_atractivos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Atractivo Turístico"), on_sort=lambda e: self._cambiar_orden_y_recargar(TIPO_ATRACTIVO, "a.nombre_atractivo", e.ascending)),
                ft.DataColumn(ft.Text("Categoría/Tipo")),
                ft.DataColumn(ft.Text("Municipio")),
                ft.DataColumn(ft.Text("Acciones"), numeric=True)
            ],
            rows=[],
            data_row_min_height=50,
            heading_row_height=40,
            show_checkbox_column=False,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=6,
            expand=False,
        )
        self.loading_atractivos = ft.ProgressRing(width=20, height=20, visible=False, stroke_width=2.5)
        self.pag_atractivos_controls_container = ft.Row()

        # --- Sección Empresas ---
        self.txt_filtro_nombre_empresa = ft.TextField(label="Buscar Empresa por Nombre", dense=True, width=250, on_submit=lambda e: self._aplicar_filtros_y_cargar_listados_ciudadano(TIPO_EMPRESA))
        self.dd_filtro_tipo_prestador_empresa = ft.Dropdown(label="Tipo de Prestador", options=[ft.dropdown.Option("", "Todos")], dense=True, width=220, on_change=lambda e: self._aplicar_filtros_y_cargar_listados_ciudadano(TIPO_EMPRESA))
        self.tabla_empresas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre / Razón Social"), on_sort=lambda e: self._cambiar_orden_y_recargar(TIPO_EMPRESA, "e.razon_social_o_nombre_comercial", e.ascending)),
                ft.DataColumn(ft.Text("Tipo Prestador")),
                ft.DataColumn(ft.Text("Municipio")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Acciones"), numeric=True)
            ],
            rows=[],
            data_row_min_height=50,
            heading_row_height=40,
            show_checkbox_column=False,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=6,
            expand=False,
        )
        self.loading_empresas = ft.ProgressRing(width=20, height=20, visible=False, stroke_width=2.5)
        self.pag_empresas_controls_container = ft.Row()

        self.mensaje_general_vista = ft.Text(
            "Seleccione un departamento y municipio para explorar la oferta turística.",
            style=ft.TextThemeStyle.TITLE_MEDIUM,
            text_align=ft.TextAlign.CENTER,
            visible=True,
            color=ft.colors.OUTLINE
        )

    def did_mount(self):
        self.page.dialog = self.dialogo_detalle
        self._cargar_departamentos_globales()
        # Pre-seleccionar si hay municipio en la sesión
        if self.selected_municipio_codigo:
            muni_info = db_manager.obtener_municipio_por_codigo(self.selected_municipio_codigo)
            if muni_info:
                self.selected_departamento_codigo = muni_info['codigo_departamento']
                self.dd_departamento_global.value = self.selected_departamento_codigo
                self._cargar_municipios_globales(self.selected_departamento_codigo, set_default_value=True)
        else:
            self._toggle_list_visibility(show_message=True)

    def _toggle_list_visibility(self, show_message: bool):
        self.mensaje_general_vista.visible = show_message
        # Ocultar o mostrar las pestañas/secciones
        if self.controls and isinstance(self.controls[0], ft.Column):
            tabs_control = self.controls[0].controls[-1]
            if isinstance(tabs_control, ft.Tabs):
                tabs_control.visible = not show_message
        self.update()

    def _cargar_departamentos_globales(self):
        self.departamentos_options = [ft.dropdown.Option(d['codigo_departamento'], d['nombre_departamento']) for d in db_manager.obtener_departamentos()]
        self.dd_departamento_global.options = self.departamentos_options
        self.update()

    def _on_departamento_global_change(self, e):
        self.selected_departamento_codigo = e.control.value
        self.dd_municipio_global.disabled = True
        self.dd_municipio_global.value = None
        self.dd_municipio_global.options = [ft.dropdown.Option("", "Cargando...")]
        self.loading_selector_muni.visible = True
        self.update()
        self._cargar_municipios_globales(self.selected_departamento_codigo)

    def _cargar_municipios_globales(self, depto_code: str, set_default_value: bool = False):
        self.municipios_options = [ft.dropdown.Option(m['codigo_municipio'], m['nombre_municipio']) for m in db_manager.obtener_municipios_por_departamento(depto_code)]
        self.dd_municipio_global.options = [ft.dropdown.Option("", "--Seleccione Municipio--")] + self.municipios_options
        self.dd_municipio_global.disabled = False
        if set_default_value:
             self.dd_municipio_global.value = self.selected_municipio_codigo
             self._aplicar_filtros_y_cargar_listados_ciudadano() # Cargar datos para el municipio por defecto
        self.loading_selector_muni.visible = False
        self.update()

    def _on_municipio_global_change(self, e):
        self.selected_municipio_codigo = e.control.value
        self._aplicar_filtros_y_cargar_listados_ciudadano()

    def _aplicar_filtros_y_cargar_listados_ciudadano(self, tipo_a_cargar: str | None = None):
        if not self.selected_municipio_codigo:
            self._toggle_list_visibility(show_message=True)
            return

        self._toggle_list_visibility(show_message=False)

        if tipo_a_cargar == TIPO_ATRACTIVO or tipo_a_cargar is None:
            self.current_page[TIPO_ATRACTIVO] = 1
            self.filtros_aplicados_atractivos = {
                "nombre__icontains": self.txt_filtro_nombre_atractivo.value or None,
                "tipo_categoria_principal": self.dd_filtro_tipo_categoria_atractivo.value or None,
                "codigo_municipio": self.selected_municipio_codigo,
            }
            self.filtros_aplicados_atractivos = {k: v for k, v in self.filtros_aplicados_atractivos.items() if v is not None}
            self._cargar_listado_paginado_ciudadano(TIPO_ATRACTIVO)

        if tipo_a_cargar == TIPO_EMPRESA or tipo_a_cargar is None:
            self.current_page[TIPO_EMPRESA] = 1
            self.filtros_aplicados_empresas = {
                "razon_social__icontains": self.txt_filtro_nombre_empresa.value or None,
                "tipo_prestador": self.dd_filtro_tipo_prestador_empresa.value or None,
                "codigo_municipio": self.selected_municipio_codigo,
            }
            self.filtros_aplicados_empresas = {k: v for k, v in self.filtros_aplicados_empresas.items() if v is not None}
            self._cargar_listado_paginado_ciudadano(TIPO_EMPRESA)
        self.update()

    def _cargar_listado_paginado_ciudadano(self, tipo_entidad: str):
        # Lógica de carga... (Simulada por ahora)
        loading_control = self.loading_atractivos if tipo_entidad == TIPO_ATRACTIVO else self.loading_empresas
        table_control = self.tabla_atractivos if tipo_entidad == TIPO_ATRACTIVO else self.tabla_empresas

        loading_control.visible = True
        table_control.rows.clear()
        self.update()

        offset = (self.current_page[tipo_entidad] - 1) * self.items_per_page
        resultados, total_items = [], 0

        if tipo_entidad == TIPO_ATRACTIVO:
            resultados, total_items = db_manager.listar_atractivos_publicos_paginado(
                filtros=self.filtros_aplicados_atractivos,
                orden=self.orden_actual_atractivos,
                limit=self.items_per_page,
                offset=offset
            )
        elif tipo_entidad == TIPO_EMPRESA:
            # Reutilizamos la función de admin, pero en un caso real podría ser una función
            # específica para la vista pública que solo muestre campos aprobados.
            resultados, total_items = db_manager.listar_empresas_paginado_admin(
                filtros=self.filtros_aplicados_empresas,
                orden=self.orden_actual_empresas,
                limit=self.items_per_page,
                offset=offset
            )

        self.total_items[tipo_entidad] = total_items

        if not resultados:
            table_control.rows.append(ft.DataRow([ft.DataCell(ft.Text(f"No se encontraron {tipo_entidad} para este municipio.",
                                                                      font_style=ft.FontStyle.ITALIC),
                                                              colspan=len(table_control.columns))]))
        else:
            for item in resultados:
                if tipo_entidad == TIPO_ATRACTIVO:
                    table_control.rows.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item.get("nombre_atractivo"))),
                            ft.DataCell(ft.Text(item.get("tipo_categoria_principal"))),
                            ft.DataCell(ft.Text(item.get("nombre_municipio"))),
                            ft.DataCell(ft.IconButton(ft.icons.INFO_OUTLINE, on_click=self.ver_detalle_atractivo, data=item)),
                        ]
                    ))
                elif tipo_entidad == TIPO_EMPRESA:
                     table_control.rows.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item.get("razon_social_o_nombre_comercial"))),
                            ft.DataCell(ft.Text(item.get("tipo_prestador"))),
                            ft.DataCell(ft.Text(item.get("nombre_municipio"))),
                            ft.DataCell(ft.Text(item.get("telefonos_contacto"))),
                            ft.DataCell(ft.IconButton(ft.icons.INFO_OUTLINE, on_click=self.ver_detalle_empresa, data=item)),
                        ]
                    ))
                # Añadir lógica para TIPO_ATRACTIVO aquí

        loading_control.visible = False
        self._actualizar_controles_paginacion(tipo_entidad)
        self.update()

    def _actualizar_controles_paginacion(self, tipo_entidad: str):
        container = self.pag_atractivos_controls_container if tipo_entidad == TIPO_ATRACTIVO else self.pag_empresas_controls_container
        container.controls.clear()

        total_pages = math.ceil(self.total_items[tipo_entidad] / self.items_per_page)
        current_page = self.current_page[tipo_entidad]

        if total_pages > 1:
            container.controls.append(ft.IconButton(
                icon=ft.icons.KEYBOARD_ARROW_LEFT,
                on_click=lambda e, t=tipo_entidad: self._cambiar_pagina_listado(e, -1, t),
                disabled=(current_page == 1)
            ))
            container.controls.append(ft.Text(f"Página {current_page} de {total_pages}"))
            container.controls.append(ft.IconButton(
                icon=ft.icons.KEYBOARD_ARROW_RIGHT,
                on_click=lambda e, t=tipo_entidad: self._cambiar_pagina_listado(e, 1, t),
                disabled=(current_page == total_pages)
            ))
        self.update()

    def _cambiar_pagina_listado(self, e, cambio, tipo_entidad):
        self.current_page[tipo_entidad] += cambio
        self._cargar_listado_paginado_ciudadano(tipo_entidad)

    def _cambiar_orden_y_recargar(self, tipo_entidad: str, columna_sort: str, ascendente: bool):
        orden = {columna_sort: "ASC" if ascendente else "DESC"}
        if tipo_entidad == TIPO_ATRACTIVO:
            self.orden_actual_atractivos = orden
        else:
            self.orden_actual_empresas = orden

        self.current_page[tipo_entidad] = 1
        self._cargar_listado_paginado_ciudadano(tipo_entidad)

    def _mostrar_dialogo_detalle(self, title: str, content_controls: list):
        self.dialogo_detalle.title = ft.Text(title)
        self.dialogo_detalle.content = ft.Column(content_controls, scroll=ft.ScrollMode.ADAPTIVE, tight=True)
        self.dialogo_detalle.actions = [
            ft.TextButton("Cerrar", on_click=lambda e: setattr(self.dialogo_detalle, 'open', False) or self.update())
        ]
        self.dialogo_detalle.open = True
        self.update()

    def _crear_fila_detalle(self, icono, etiqueta, valor):
        return ft.Row([
            ft.Icon(icono, size=16, color=ft.colors.OUTLINE),
            ft.Text(f"{etiqueta}:", weight=ft.FontWeight.BOLD),
            ft.Text(valor, selectable=True)
        ], spacing=10)

    def ver_detalle_atractivo(self, e):
        atractivo = e.control.data
        content = [
            self._crear_fila_detalle(ft.icons.CATEGORY, "Categoría", atractivo.get("tipo_categoria_principal")),
            self._crear_fila_detalle(ft.icons.DESCRIPTION, "Descripción", atractivo.get("descripcion_breve", "No disponible.")),
            self._crear_fila_detalle(ft.icons.LOCATION_CITY, "Municipio", atractivo.get("nombre_municipio")),
        ]
        self._mostrar_dialogo_detalle(f"Detalle: {atractivo.get('nombre_atractivo')}", content)

    def ver_detalle_empresa(self, e):
        empresa = e.control.data
        content = [
            self._crear_fila_detalle(ft.icons.STOREFRONT, "Tipo", empresa.get("tipo_prestador")),
            self._crear_fila_detalle(ft.icons.DIALPAD, "Teléfono", empresa.get("telefonos_contacto")),
            self._crear_fila_detalle(ft.icons.EMAIL, "Email", empresa.get("email_contacto")),
            self._crear_fila_detalle(ft.icons.WEB, "Web", empresa.get("pagina_web")),
            self._crear_fila_detalle(ft.icons.LOCATION_ON, "Dirección", empresa.get("direccion_principal")),
            ft.Divider(),
            ft.Text(empresa.get("descripcion_servicios", "No hay descripción disponible.")),
        ]
        self._mostrar_dialogo_detalle(f"Detalle: {empresa.get('razon_social_o_nombre_comercial')}", content)

    def build(self):
        selectores_ubicacion = ft.Row(
            [self.dd_departamento_global, self.dd_municipio_global, self.loading_selector_muni],
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True
        )

        seccion_atractivos_ui = ft.Column([
            ft.Text("Atractivos Turísticos del Municipio", style=ft.TextThemeStyle.TITLE_LARGE),
            ft.ResponsiveRow([
                ft.Column([self.txt_filtro_nombre_atractivo], col={"sm": 12, "md": 5}),
                ft.Column([self.dd_filtro_tipo_categoria_atractivo], col={"sm": 12, "md": 5}),
            ], vertical_alignment=ft.CrossAxisAlignment.END),
            ft.Row([self.loading_atractivos], alignment=ft.MainAxisAlignment.CENTER),
            self.tabla_atractivos,
            self.pag_atractivos_controls_container
        ], spacing=10)

        seccion_empresas_ui = ft.Column([
            ft.Text("Empresas y Prestadores de Servicios", style=ft.TextThemeStyle.TITLE_LARGE),
            ft.ResponsiveRow([
                ft.Column([self.txt_filtro_nombre_empresa], col={"sm": 12, "md": 5}),
                ft.Column([self.dd_filtro_tipo_prestador_empresa], col={"sm": 12, "md": 5}),
            ], vertical_alignment=ft.CrossAxisAlignment.END),
            ft.Row([self.loading_empresas], alignment=ft.MainAxisAlignment.CENTER),
            self.tabla_empresas,
            self.pag_empresas_controls_container
        ], spacing=10)

        return ft.Column(
            [
                ft.Text("Explora la Oferta Turística", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                selectores_ubicacion,
                ft.Divider(height=15),
                self.mensaje_general_vista,
                ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(text="Atractivos", icon=ft.icons.PALETTE_OUTLINED, content=ft.Container(seccion_atractivos_ui, padding=10)),
                        ft.Tab(text="Empresas/PST", icon=ft.icons.STOREFRONT_OUTLINED, content=ft.Container(seccion_empresas_ui, padding=10)),
                    ],
                    expand=True,
                    visible=not self.mensaje_general_vista.visible
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            padding=ft.padding.symmetric(vertical=10, horizontal=20),
            spacing=15
        )
