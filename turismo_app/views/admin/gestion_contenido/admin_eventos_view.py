import flet as ft
from turismo_app.database import db_manager
import datetime

class AdminEventosView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")
        self.evento_id_actual_edicion = None

        # === FORMULARIO DE EVENTO ===
        self.txt_nombre_evento = ft.TextField(label="Nombre del Evento*", dense=True)
        self.txt_descripcion = ft.TextField(label="Descripción", multiline=True, min_lines=3, dense=True)

        self.dp_fecha_inicio = ft.DatePicker(on_change=lambda e: self._on_date_change(e, self.btn_fecha_inicio, "Inicio"))
        self.btn_fecha_inicio = ft.OutlinedButton("Fecha de Inicio", icon=ft.icons.CALENDAR_TODAY, on_click=lambda _: self.page.open(self.dp_fecha_inicio))

        self.dp_fecha_fin = ft.DatePicker(on_change=lambda e: self._on_date_change(e, self.btn_fecha_fin, "Fin"))
        self.btn_fecha_fin = ft.OutlinedButton("Fecha de Fin", icon=ft.icons.CALENDAR_TODAY, on_click=lambda _: self.page.open(self.dp_fecha_fin))

        self.sw_publicado = ft.Switch(label="Publicar Evento", value=False)

        self.btn_guardar = ft.ElevatedButton(text="Guardar Nuevo Evento", on_click=self._guardar_handler, icon=ft.icons.SAVE)
        self.btn_limpiar = ft.TextButton(text="Limpiar", on_click=self._limpiar_formulario, icon=ft.icons.CLEAR_ALL)

        # === LISTADO DE EVENTOS ===
        self.txt_filtro_nombre = ft.TextField(label="Buscar por nombre...", on_submit=self._aplicar_filtros, dense=True, expand=True)
        self.btn_aplicar_filtros = ft.IconButton(icon=ft.icons.SEARCH, on_click=self._aplicar_filtros)
        self.paginacion_controls = ft.Row()

        self.tabla_eventos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre del Evento")),
                ft.DataColumn(ft.Text("Fecha Inicio")),
                ft.DataColumn(ft.Text("Fecha Fin")),
                ft.DataColumn(ft.Text("Publicado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        self.loading_tabla = ft.ProgressRing(visible=False)
        self.current_page = 1
        self.items_per_page = 10

    def did_mount(self):
        if self.dp_fecha_inicio not in self.page.overlay:
            self.page.overlay.append(self.dp_fecha_inicio)
        if self.dp_fecha_fin not in self.page.overlay:
            self.page.overlay.append(self.dp_fecha_fin)
            self.page.update()
        self._cargar_listado_eventos()

    def _aplicar_filtros(self, e):
        self.current_page = 1
        self._cargar_listado_eventos()

    def _on_date_change(self, e, btn_control, label):
        if e.control.value:
            btn_control.text = f"{label}: {e.control.value.strftime('%Y-%m-%d')}"
        self.update()

    def _cargar_listado_eventos(self):
        self.tabla_eventos.rows.clear()
        self.loading_tabla.visible = True
        self.update()

        offset = (self.current_page - 1) * self.items_per_page
        filtros = {
            "codigo_municipio": self.codigo_municipio_admin,
            "nombre_evento__icontains": self.txt_filtro_nombre.value or None
        }

        eventos, total_items = db_manager.listar_eventos_admin_paginado(
            filtros={k: v for k, v in filtros.items() if v is not None},
            orden={},
            limit=self.items_per_page,
            offset=offset
        )

        self.loading_tabla.visible = False
        if not eventos:
            self.tabla_eventos.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("No hay eventos registrados para este municipio."), colspan=5)])
            )
        else:
            for evento in eventos:
                self.tabla_eventos.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(evento.get("nombre_evento"))),
                        ft.DataCell(ft.Text(evento.get("fecha_inicio"))),
                        ft.DataCell(ft.Text(evento.get("fecha_fin"))),
                        ft.DataCell(ft.Icon(ft.icons.CHECK if evento.get("publicado") else ft.icons.CLOSE)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar", data=evento, on_click=self._cargar_para_edicion),
                        ])),
                    ])
                )

        self._actualizar_paginacion(total_items)
        self.update()

    def _guardar_handler(self, e):
        if not self.txt_nombre_evento.value:
            self.txt_nombre_evento.error_text = "Campo obligatorio"
            self.update()
            return

        datos = {
            "nombre_evento": self.txt_nombre_evento.value,
            "descripcion": self.txt_descripcion.value,
            "fecha_inicio": self.dp_fecha_inicio.value.isoformat() if self.dp_fecha_inicio.value else None,
            "fecha_fin": self.dp_fecha_fin.value.isoformat() if self.dp_fecha_fin.value else None,
            "publicado": self.sw_publicado.value,
            "codigo_municipio": self.codigo_municipio_admin,
        }

        db_manager.crear_o_actualizar_evento(datos, self.evento_id_actual_edicion)

        self._limpiar_formulario()
        self._cargar_listado_eventos()

    def _cargar_para_edicion(self, e):
        data = e.control.data
        self.evento_id_actual_edicion = data.get("id_evento")
        self.txt_nombre_evento.value = data.get("nombre_evento")
        self.txt_descripcion.value = data.get("descripcion")
        if data.get("fecha_inicio"):
            self.dp_fecha_inicio.value = datetime.date.fromisoformat(data.get("fecha_inicio"))
            self.btn_fecha_inicio.text = f"Inicio: {self.dp_fecha_inicio.value.strftime('%Y-%m-%d')}"
        if data.get("fecha_fin"):
            self.dp_fecha_fin.value = datetime.date.fromisoformat(data.get("fecha_fin"))
            self.btn_fecha_fin.text = f"Fin: {self.dp_fecha_fin.value.strftime('%Y-%m-%d')}"
        self.sw_publicado.value = data.get("publicado", False)
        self.btn_guardar.text = "Actualizar Evento"
        self.update()

    def _limpiar_formulario(self, e=None):
        self.evento_id_actual_edicion = None
        self.txt_nombre_evento.value = ""
        self.txt_descripcion.value = ""
        self.dp_fecha_inicio.value = None
        self.dp_fecha_fin.value = None
        self.btn_fecha_inicio.text = "Fecha de Inicio"
        self.btn_fecha_fin.text = "Fecha de Fin"
        self.sw_publicado.value = False
        self.txt_nombre_evento.error_text = None
        self.btn_guardar.text = "Guardar Nuevo Evento"
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
        self._cargar_listado_eventos()

    def build(self):
        formulario = ft.Container(
            content=ft.Column([
                ft.Text("Formulario de Evento Turístico", style=ft.TextThemeStyle.TITLE_LARGE),
                self.txt_nombre_evento,
                self.txt_descripcion,
                ft.Row([self.btn_fecha_inicio, self.btn_fecha_fin]),
                self.sw_publicado,
                ft.Row([self.btn_guardar, self.btn_limpiar], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=20
        )

        listado = ft.Column(
            [
                ft.Text("Listado de Eventos", style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Row([self.txt_filtro_nombre, self.btn_aplicar_filtros]),
                self.loading_tabla,
                self.tabla_eventos,
                self.paginacion_controls,
            ],
            spacing=10
        )

        return ft.Column([
            ft.Text("Gestión de Eventos Turísticos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Formulario", icon=ft.icons.EVENT, content=formulario),
                    ft.Tab(text="Listado", icon=ft.icons.LIST_ALT, content=listado),
                ],
                expand=True
            )
        ])
