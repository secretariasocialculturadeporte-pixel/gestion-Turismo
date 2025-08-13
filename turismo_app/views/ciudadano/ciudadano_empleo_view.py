import flet as ft
from turismo_app.database import db_manager
import datetime
import math
import time

class CiudadanoEmpleoView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.dialogo_detalle_vacante = ft.AlertDialog(
            modal=True,
            title=ft.Text("Detalle de la Oportunidad de Empleo"),
            actions_alignment=ft.MainAxisAlignment.END
        )
        # Estado de selección y filtros
        self.departamentos_options_empleo = []
        self.municipios_options_empleo = []
        self.selected_departamento_codigo_empleo = None
        self.selected_municipio_codigo_empleo = page.session.get("user_codigo_municipio")
        self.filtros_aplicados_vacantes = {}
        self.orden_actual_vacantes = {"v.fecha_publicacion": "DESC"}

        # Paginación
        self.current_page_vac_ciudadano = 1
        self.items_per_page_vac_ciudadano = 8
        self.total_items_vac_ciudadano = 0

        # --- Controles de Selección de Ubicación ---
        self.dd_departamento_global_empleo = ft.Dropdown(
            label="Departamento donde buscar empleo",
            hint_text="Seleccione...",
            options=[],
            on_change=self._on_departamento_global_empleo_change,
            width=280,
            dense=True,
            content_padding=8
        )
        self.dd_municipio_global_empleo = ft.Dropdown(
            label="Municipio donde buscar empleo",
            hint_text="Primero seleccione depto.",
            options=[ft.dropdown.Option("", "--Seleccione Depto.--")],
            on_change=self._on_municipio_global_empleo_change,
            disabled=True,
            width=280,
            dense=True,
            content_padding=8
        )
        self.loading_selector_muni_emp = ft.ProgressRing(width=16, height=16, visible=False, stroke_width=2)

        # --- Filtros Avanzados para Vacantes ---
        self.txt_filtro_palabra_clave_vac = ft.TextField(
            label="Palabra Clave (Título, Descripción, Requisitos)",
            dense=True,
            width=350,
            on_submit=self._aplicar_filtros_y_cargar_vacantes,
            prefix_icon=ft.icons.SEARCH
        )
        TIPOS_CONTRATO_OPTIONS = [
            ft.dropdown.Option("", "Todos los Tipos"),
            ft.dropdown.Option("INDEFINIDO"),
            ft.dropdown.Option("TERMINO_FIJO"),
            ft.dropdown.Option("PRESTACION_SERVICIOS"),
            ft.dropdown.Option("APRENDIZAJE"),
            ft.dropdown.Option("TEMPORAL_OBRA_LABOR"),
            ft.dropdown.Option("OTRO_CONTRATO")
        ]
        self.dd_filtro_tipo_contrato_vac_ciudadano = ft.Dropdown(
            label="Tipo de Contrato",
            dense=True,
            width=220,
            options=TIPOS_CONTRATO_OPTIONS,
            on_change=self._aplicar_filtros_y_cargar_vacantes
        )
        self.btn_limpiar_filtros_vac_ciudadano = ft.IconButton(
            ft.icons.FILTER_LIST_OFF_ROUNDED,
            tooltip="Limpiar Filtros de Búsqueda",
            on_click=self._limpiar_filtros_vac_handler
        )
        self.tabla_vacantes = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Título de la Vacante"), on_sort=lambda e: self._cambiar_orden_y_recargar_vacantes("v.titulo_vacante", e.ascending)),
                ft.DataColumn(ft.Text("Empleador")),
                ft.DataColumn(ft.Text("Municipio"), on_sort=lambda e: self._cambiar_orden_y_recargar_vacantes("m.nombre_municipio", e.ascending)),
                ft.DataColumn(ft.Text("Publicada"), on_sort=lambda e: self._cambiar_orden_y_recargar_vacantes("v.fecha_publicacion", e.ascending)),
                ft.DataColumn(ft.Text("Detalles"), numeric=True)
            ],
            rows=[],
            data_row_min_height=50,
            heading_row_height=40,
            show_checkbox_column=False,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=6,
            expand=False
        )
        self.pag_vac_controls_container = ft.Row()
        self.loading_listado_empleo = ft.ProgressRing(width=22, height=22, visible=False)
        self.mensaje_estado_empleo = ft.Text(
            "Utilice los selectores de arriba para encontrar oportunidades de empleo en el municipio de su interés.",
            italic=True,
            color=ft.colors.OUTLINE,
            size=14,
            text_align=ft.TextAlign.CENTER,
            visible=True
        )

    def did_mount(self):
        self.page.dialog = self.dialogo_detalle_vacante
        self._cargar_departamentos_globales_empleo()
        if self.selected_municipio_codigo_empleo:
            muni_info = db_manager.obtener_municipio_por_codigo(self.selected_municipio_codigo_empleo)
            if muni_info:
                self.selected_departamento_codigo_empleo = muni_info['codigo_departamento']
                self.dd_departamento_global_empleo.value = self.selected_departamento_codigo_empleo
                self._cargar_municipios_globales_empleo(self.selected_departamento_codigo_empleo, set_default_value=True)
        else:
            self._toggle_list_visibility(show_message=True)
        self.update()

    def _toggle_list_visibility(self, show_message: bool):
        self.mensaje_estado_empleo.visible = show_message
        self.tabla_vacantes.visible = not show_message
        self.pag_vac_controls_container.visible = not show_message
        self.update()

    def _cargar_departamentos_globales_empleo(self):
        self.departamentos_options_empleo = [ft.dropdown.Option(d['codigo_departamento'], d['nombre_departamento']) for d in db_manager.obtener_departamentos()]
        self.dd_departamento_global_empleo.options = self.departamentos_options_empleo
        self.update()

    def _on_departamento_global_empleo_change(self, e):
        self.selected_departamento_codigo_empleo = e.control.value
        self.dd_municipio_global_empleo.disabled = True
        self.dd_municipio_global_empleo.value = None
        self.dd_municipio_global_empleo.options = [ft.dropdown.Option("", "Cargando...")]
        self.loading_selector_muni_emp.visible = True
        self.update()
        self._cargar_municipios_globales_empleo(self.selected_departamento_codigo_empleo)

    def _cargar_municipios_globales_empleo(self, depto_code: str, set_default_value: bool = False):
        self.municipios_options_empleo = [ft.dropdown.Option(m['codigo_municipio'], m['nombre_municipio']) for m in db_manager.obtener_municipios_por_departamento(depto_code)]
        self.dd_municipio_global_empleo.options = [ft.dropdown.Option("", "--Seleccione Municipio--")] + self.municipios_options_empleo
        self.dd_municipio_global_empleo.disabled = False
        if set_default_value:
            self.dd_municipio_global_empleo.value = self.selected_municipio_codigo_empleo
            self._aplicar_filtros_y_cargar_vacantes()
        self.loading_selector_muni_emp.visible = False
        self.update()

    def _on_municipio_global_empleo_change(self, e):
        self.selected_municipio_codigo_empleo = e.control.value
        self._aplicar_filtros_y_cargar_vacantes()

    def _aplicar_filtros_y_cargar_vacantes(self, e=None):
        self.current_page_vac_ciudadano = 1
        self._cargar_listado_vacantes_ciudadano()

    def _limpiar_filtros_vac_handler(self, e):
        self.txt_filtro_palabra_clave_vac.value = ""
        self.dd_filtro_tipo_contrato_vac_ciudadano.value = ""
        self.update()
        self._aplicar_filtros_y_cargar_vacantes()

    def _cargar_listado_vacantes_ciudadano(self):
        if not self.selected_municipio_codigo_empleo:
            self._toggle_list_visibility(show_message=True)
            return

        self._toggle_list_visibility(show_message=False)
        self.loading_listado_empleo.visible = True
        self.tabla_vacantes.rows.clear()
        self.update()

        self.filtros_aplicados_vacantes = {
            "codigo_municipio": self.selected_municipio_codigo_empleo,
            "tipo_contrato": self.dd_filtro_tipo_contrato_vac_ciudadano.value or None,
            "palabra_clave": self.txt_filtro_palabra_clave_vac.value or None,
        }
        self.filtros_aplicados_vacantes = {k: v for k, v in self.filtros_aplicados_vacantes.items() if v is not None}

        offset = (self.current_page_vac_ciudadano - 1) * self.items_per_page_vac_ciudadano

        resultados, total_items = db_manager.listar_vacantes_publicas_paginado(
            filtros=self.filtros_aplicados_vacantes,
            orden=self.orden_actual_vacantes,
            limit=self.items_per_page_vac_ciudadano,
            offset=offset
        )

        self.total_items_vac_ciudadano = total_items
        if not resultados:
            self.tabla_vacantes.rows.append(ft.DataRow([ft.DataCell(ft.Text("No se encontraron vacantes con estos criterios.",
                                                                            font_style=ft.FontStyle.ITALIC),
                                                                            colspan=len(self.tabla_vacantes.columns))]))
        else:
            for vacante in resultados:
                self.tabla_vacantes.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(vacante.get("titulo_vacante"))),
                        ft.DataCell(ft.Text(vacante.get("nombre_empleador") or vacante.get("nombre_empleador_alternativo", "N/A"))),
                        ft.DataCell(ft.Text(vacante.get("nombre_municipio"))),
                        ft.DataCell(ft.Text(datetime.datetime.fromisoformat(vacante.get("fecha_publicacion")).strftime("%Y-%m-%d"))),
                        ft.DataCell(ft.IconButton(ft.icons.INFO_OUTLINE, on_click=self.ver_detalle_vacante, data=vacante)),
                    ])
                )

        self.loading_listado_empleo.visible = False
        self._actualizar_controles_paginacion_vacantes()
        self.update()

    def _actualizar_controles_paginacion_vacantes(self):
        container = self.pag_vac_controls_container
        container.controls.clear()
        total_pages = math.ceil(self.total_items_vac_ciudadano / self.items_per_page_vac_ciudadano)
        current_page = self.current_page_vac_ciudadano
        if total_pages > 1:
            container.controls.append(ft.IconButton(icon=ft.icons.KEYBOARD_ARROW_LEFT, on_click=lambda e: self._cambiar_pagina_vacantes(e, -1), disabled=(current_page == 1)))
            container.controls.append(ft.Text(f"Página {current_page} de {total_pages}"))
            container.controls.append(ft.IconButton(icon=ft.icons.KEYBOARD_ARROW_RIGHT, on_click=lambda e: self._cambiar_pagina_vacantes(e, 1), disabled=(current_page == total_pages)))
        self.update()

    def _cambiar_pagina_vacantes(self, e, cambio):
        self.current_page_vac_ciudadano += cambio
        self._cargar_listado_vacantes_ciudadano()

    def _cambiar_orden_y_recargar_vacantes(self, columna_sort_db: str, ascendente: bool):
        self.orden_actual_vacantes = {columna_sort_db: "ASC" if ascendente else "DESC"}
        self.current_page_vac_ciudadano = 1
        self._cargar_listado_vacantes_ciudadano()

    def ver_detalle_vacante(self, e):
        # TODO: Implementar diálogo de detalle
        print("Ver detalle de vacante:", e.control.data)
        pass

    def build(self):
        controles_filtros_ubicacion_emp = ft.ResponsiveRow(
            [
                ft.Column([self.dd_departamento_global_empleo], col={"sm": 12, "md": 6}),
                ft.Column([self.dd_municipio_global_empleo], col={"sm": 12, "md": 6}),
                self.loading_selector_muni_emp
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        controles_filtros_vac = ft.ResponsiveRow(
            [
                ft.Column([self.txt_filtro_palabra_clave_vac], col={"sm": 12, "md": 7}),
                ft.Column([self.dd_filtro_tipo_contrato_vac_ciudadano], col={"sm": 12, "md": 4}),
                ft.Column([self.btn_limpiar_filtros_vac_ciudadano], col={"sm": 12, "md": 1}),
            ],
            vertical_alignment=ft.CrossAxisAlignment.END
        )
        return ft.Column(
            [
                ft.Text("Oportunidades de Empleo en el Sector Turístico", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                controles_filtros_ubicacion_emp,
                ft.Divider(),
                controles_filtros_vac,
                ft.Row([self.loading_listado_empleo], alignment=ft.MainAxisAlignment.CENTER),
                self.mensaje_estado_empleo,
                ft.Container(content=self.tabla_vacantes, expand=False),
                self.pag_vac_controls_container,
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            padding=20,
            spacing=15
        )
