import flet as ft
from turismo_app.database import db_manager
import datetime

class AdminIniciativasView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")
        self.iniciativa_id_actual_edicion = None

        # === FORMULARIO DE INICIATIVA ===
        self.txt_nombre_iniciativa = ft.TextField(label="Nombre de la Iniciativa*", dense=True)
        self.dd_tipo_iniciativa = ft.Dropdown(
            label="Tipo de Iniciativa*",
            options=[
                ft.dropdown.Option("PLAN", "Plan"),
                ft.dropdown.Option("PROGRAMA", "Programa"),
                ft.dropdown.Option("PROYECTO", "Proyecto"),
                ft.dropdown.Option("POLITICA", "Política Pública"),
                ft.dropdown.Option("OTRA", "Otra"),
            ],
            dense=True
        )
        self.txt_descripcion = ft.TextField(label="Descripción / Objetivos", multiline=True, min_lines=3, dense=True)
        self.dd_estado = ft.Dropdown(
            label="Estado Actual",
            options=[
                ft.dropdown.Option("FORMULACION", "En Formulación"),
                ft.dropdown.Option("EJECUCION", "En Ejecución"),
                ft.dropdown.Option("TERMINADO", "Terminado"),
                ft.dropdown.Option("CANCELADO", "Cancelado"),
            ],
            dense=True
        )
        self.txt_presupuesto = ft.TextField(label="Presupuesto Asignado (COP)", prefix_text="$", keyboard_type=ft.KeyboardType.NUMBER, dense=True)

        self.btn_guardar = ft.ElevatedButton(text="Guardar Nueva Iniciativa", on_click=self._guardar_handler, icon=ft.icons.SAVE)
        self.btn_limpiar = ft.TextButton(text="Limpiar", on_click=self._limpiar_formulario, icon=ft.icons.CLEAR_ALL)

        # === LISTADO DE INICIATIVAS ===
        self.txt_filtro_nombre = ft.TextField(label="Buscar por nombre...", on_submit=self._aplicar_filtros, dense=True, expand=True)
        self.btn_aplicar_filtros = ft.IconButton(icon=ft.icons.SEARCH, on_click=self._aplicar_filtros)
        self.paginacion_controls = ft.Row()

        self.tabla_iniciativas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        self.loading_tabla = ft.ProgressRing(visible=False)
        self.current_page = 1
        self.items_per_page = 10

    def did_mount(self):
        self._cargar_listado_iniciativas()

    def _aplicar_filtros(self, e):
        self.current_page = 1
        self._cargar_listado_iniciativas()

    def _cargar_listado_iniciativas(self):
        self.tabla_iniciativas.rows.clear()
        self.loading_tabla.visible = True
        self.update()

        offset = (self.current_page - 1) * self.items_per_page
        filtros = {
            "codigo_municipio": self.codigo_municipio_admin,
            "nombre_iniciativa__icontains": self.txt_filtro_nombre.value or None
        }

        iniciativas, total_items = db_manager.listar_iniciativas_admin_paginado(
            filtros={k: v for k, v in filtros.items() if v is not None},
            orden={},
            limit=self.items_per_page,
            offset=offset
        )

        self.loading_tabla.visible = False
        if not iniciativas:
            self.tabla_iniciativas.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("No hay iniciativas registradas para este municipio."), colspan=4)])
            )
        else:
            for iniciativa in iniciativas:
                self.tabla_iniciativas.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(iniciativa.get("nombre_iniciativa"))),
                        ft.DataCell(ft.Text(iniciativa.get("tipo_iniciativa"))),
                        ft.DataCell(ft.Text(iniciativa.get("estado"))),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar", data=iniciativa, on_click=self._cargar_para_edicion),
                        ])),
                    ])
                )
        self._actualizar_paginacion(total_items)
        self.update()

    def _guardar_handler(self, e):
        if not self.txt_nombre_iniciativa.value or not self.dd_tipo_iniciativa.value:
            self.txt_nombre_iniciativa.error_text = "Campo obligatorio"
            self.update()
            return

        datos = {
            "nombre_iniciativa": self.txt_nombre_iniciativa.value,
            "tipo_iniciativa": self.dd_tipo_iniciativa.value,
            "descripcion": self.txt_descripcion.value,
            "estado": self.dd_estado.value,
            "presupuesto": self.txt_presupuesto.value,
            "codigo_municipio": self.codigo_municipio_admin,
        }

        db_manager.crear_o_actualizar_iniciativa(datos, self.iniciativa_id_actual_edicion)

        self._limpiar_formulario()
        self._cargar_listado_iniciativas()

    def _cargar_para_edicion(self, e):
        data = e.control.data
        self.iniciativa_id_actual_edicion = data.get("id_iniciativa")
        self.txt_nombre_iniciativa.value = data.get("nombre_iniciativa")
        self.dd_tipo_iniciativa.value = data.get("tipo_iniciativa")
        self.txt_descripcion.value = data.get("descripcion")
        self.dd_estado.value = data.get("estado")
        self.txt_presupuesto.value = data.get("presupuesto")
        self.btn_guardar.text = "Actualizar Iniciativa"
        self.update()

    def _actualizar_paginacion(self, total_items):
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        self.paginacion_controls.controls = []
        if total_pages > 1:
            self.paginacion_controls.controls.append(ft.IconButton(icon=ft.icons.KEYBOARD_ARROW_LEFT, on_click=lambda e: self._cambiar_pagina(e, -1), disabled=(self.current_page == 1)))
            self.paginacion_controls.controls.append(ft.Text(f"Página {self.current_page} de {total_pages}"))
            self.paginacion_controls.controls.append(ft.IconButton(icon=ft.icons.KEYBOARD_ARROW_RIGHT, on_click=lambda e: self._cambiar_pagina(e, 1), disabled=(self.current_page == total_pages)))
        self.update()

    def _cambiar_pagina(self, e, cambio):
        self.current_page += cambio
        self._cargar_listado_iniciativas()

    def _limpiar_formulario(self, e=None):
        self.iniciativa_id_actual_edicion = None
        self.txt_nombre_iniciativa.value = ""
        self.dd_tipo_iniciativa.value = None
        self.txt_descripcion.value = ""
        self.dd_estado.value = None
        self.txt_presupuesto.value = ""
        self.txt_nombre_iniciativa.error_text = None
        self.btn_guardar.text = "Guardar Nueva Iniciativa"
        self.update()

    def build(self):
        formulario = ft.Container(
            content=ft.Column([
                ft.Text("Formulario de Iniciativa Turística", style=ft.TextThemeStyle.TITLE_LARGE),
                self.txt_nombre_iniciativa,
                self.dd_tipo_iniciativa,
                self.txt_descripcion,
                self.dd_estado,
                self.txt_presupuesto,
                ft.Row([self.btn_guardar, self.btn_limpiar], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=20
        )

        listado = ft.Column(
            [
                ft.Text("Listado de Iniciativas", style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Row([self.txt_filtro_nombre, self.btn_aplicar_filtros]),
                self.loading_tabla,
                self.tabla_iniciativas,
                self.paginacion_controls,
            ],
            spacing=10,
        )

        return ft.Column([
            ft.Text("Gestión de Iniciativas Turísticas", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Formulario", icon=ft.icons.EDIT_NOTE, content=formulario),
                    ft.Tab(text="Listado", icon=ft.icons.LIST_ALT, content=listado),
                ],
                expand=True
            )
        ])
