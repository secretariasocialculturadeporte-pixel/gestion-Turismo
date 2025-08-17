import flet as ft
from turismo_app.database import db_manager
import datetime

class EmpresaGestionProductosView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.producto_id_actual = None

        # Paginación
        self.current_page = 1
        self.items_per_page = 5

        # Controles del formulario
        self.txt_nombre = ft.TextField(label="Nombre del Producto/Evento*")
        self.txt_descripcion = ft.TextField(label="Descripción", multiline=True)
        self.dd_tipo = ft.Dropdown(
            label="Tipo*",
            options=[ft.dropdown.Option("Producto"), ft.dropdown.Option("Evento")],
            on_change=self._toggle_fecha_picker
        )
        self.txt_precio = ft.TextField(label="Precio (COP)", keyboard_type=ft.KeyboardType.NUMBER)

        self.dp_fecha_evento = ft.DatePicker(on_change=self._on_fecha_seleccionada)
        self.txt_fecha_evento = ft.TextField(label="Fecha del Evento", read_only=True, visible=False)
        self.btn_abrir_datepicker = ft.IconButton(icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.page.open(self.dp_fecha_evento), visible=False)
        self.fecha_seleccionada = None

        self.sw_activo = ft.Switch(label="Activo / Visible", value=True)
        self.btn_guardar = ft.ElevatedButton("Guardar Nuevo", on_click=self._guardar_handler)
        self.btn_limpiar = ft.OutlinedButton("Limpiar / Cancelar Edición", on_click=self._limpiar_formulario)

        # Controles del listado
        self.tabla_items = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Precio/Fecha")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )
        self.paginacion_controls = ft.Row()

    def did_mount(self):
        if self.dp_fecha_evento not in self.page.overlay:
            self.page.overlay.append(self.dp_fecha_evento)
        self._cargar_listado()

    def _toggle_fecha_picker(self, e):
        es_evento = self.dd_tipo.value == "Evento"
        self.txt_fecha_evento.visible = es_evento
        self.btn_abrir_datepicker.visible = es_evento
        self.txt_precio.visible = not es_evento
        self.page.update()

    def _on_fecha_seleccionada(self, e):
        self.fecha_seleccionada = self.dp_fecha_evento.value.strftime("%Y-%m-%d")
        self.txt_fecha_evento.value = self.fecha_seleccionada
        self.page.update()

    def _cargar_listado(self):
        offset = (self.current_page - 1) * self.items_per_page
        filtros = {"empresa_id": self.empresa_id}
        orden = {"nombre_producto_evento": "ASC"}

        resultados, total_items = db_manager.listar_productos_eventos_por_empresa_paginado(
            filtros, orden, self.items_per_page, offset
        )

        self.tabla_items.rows.clear()
        for item in resultados:
            self.tabla_items.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["nombre_producto_evento"])),
                        ft.DataCell(ft.Text(item["tipo_oferta"])),
                        ft.DataCell(ft.Text(f"{item['precio_unitario_cop']:.2f}" if item["tipo_oferta"] == "Producto" else item["fecha_inicio"])),
                        ft.DataCell(ft.Switch(value=bool(item["activo"]), disabled=True)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, on_click=self._editar_handler, data=item),
                            ft.IconButton(icon=ft.icons.DELETE, on_click=self._borrar_handler, data=item["id_producto_evento"]),
                        ])),
                    ]
                )
            )
        self._actualizar_paginacion(total_items)
        self.page.update()

    def _actualizar_paginacion(self, total_items):
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        self.paginacion_controls.controls.clear()
        for i in range(1, total_pages + 1):
            self.paginacion_controls.controls.append(
                ft.ElevatedButton(
                    text=str(i),
                    on_click=self._cambiar_pagina,
                    data=i,
                    disabled=i == self.current_page
                )
            )

    def _cambiar_pagina(self, e):
        self.current_page = e.control.data
        self._cargar_listado()

    def _guardar_handler(self, e):
        datos = {
            "empresa_id": self.empresa_id,
            "nombre_producto_evento": self.txt_nombre.value,
            "descripcion": self.txt_descripcion.value,
            "tipo_oferta": self.dd_tipo.value,
            "precio_unitario_cop": float(self.txt_precio.value) if self.dd_tipo.value == "Producto" else None,
            "fecha_inicio": self.fecha_seleccionada if self.dd_tipo.value == "Evento" else None,
            "activo": self.sw_activo.value,
            "audit_user_id": self.page.session.get("user_id")
        }

        db_manager.crear_o_actualizar_producto_evento(datos, self.producto_id_actual)
        self._limpiar_formulario()
        self._cargar_listado()

    def _limpiar_formulario(self, e=None):
        self.producto_id_actual = None
        self.txt_nombre.value = ""
        self.txt_descripcion.value = ""
        self.dd_tipo.value = None
        self.txt_precio.value = ""
        self.txt_fecha_evento.value = ""
        self.sw_activo.value = True
        self.btn_guardar.text = "Guardar Nuevo"
        self._toggle_fecha_picker(None)
        self.page.update()

    def _editar_handler(self, e):
        item = e.control.data
        self.producto_id_actual = item["id_producto_evento"]
        self.txt_nombre.value = item["nombre_producto_evento"]
        self.txt_descripcion.value = item["descripcion"]
        self.dd_tipo.value = item["tipo_oferta"]
        self.txt_precio.value = str(item["precio_unitario_cop"]) if item["precio_unitario_cop"] else ""
        self.fecha_seleccionada = item["fecha_inicio"]
        self.txt_fecha_evento.value = self.fecha_seleccionada
        self.sw_activo.value = bool(item["activo"])
        self.btn_guardar.text = "Actualizar"
        self._toggle_fecha_picker(None)
        self.page.update()

    def _borrar_handler(self, e):
        # En una app real, aquí iría un diálogo de confirmación
        db_manager.borrar_producto_evento(e.control.data)
        self._cargar_listado()

    def build(self):
        self.did_mount() # Cargar datos iniciales

        formulario = ft.Container(
            ft.Column([
                self.txt_nombre,
                self.txt_descripcion,
                self.dd_tipo,
                self.txt_precio,
                ft.Row([self.txt_fecha_evento, self.btn_abrir_datepicker]),
                self.sw_activo,
                ft.Row([self.btn_guardar, self.btn_limpiar])
            ]),
            padding=15
        )

        listado = ft.Column([self.tabla_items, self.paginacion_controls])

        return ft.Column([
            ft.Text("Gestión de Productos y Eventos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Nuevo/Editar", content=formulario),
                    ft.Tab(text="Listado", content=listado)
                ]
            )
        ])
