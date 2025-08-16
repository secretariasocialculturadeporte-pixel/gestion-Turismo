import flet as ft
from turismo_app.database import db_manager
import datetime

class AdminVacantesView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")
        self.rol_admin = page.session.get("user_rol")
        self.vacante_id_actual_edicion = None

        # === FORMULARIO DE VACANTE ===
        self.txt_titulo_vacante = ft.TextField(label="Título de la Vacante*", dense=True)
        self.dd_empresa_asociada = ft.Dropdown(label="Empresa que Ofrece la Vacante (Opcional)", dense=True) # Se poblaría desde la BD
        self.txt_empleador_alternativo = ft.TextField(label="Otro Empleador (si no está en la lista)", dense=True)
        self.txt_descripcion = ft.TextField(label="Descripción del Cargo*", multiline=True, min_lines=3, dense=True)
        self.txt_requisitos = ft.TextField(label="Requisitos", multiline=True, min_lines=2, dense=True)

        self.dd_tipo_contrato = ft.Dropdown(
            label="Tipo de Contrato",
            options=[
                ft.dropdown.Option("INDEFINIDO", "Indefinido"),
                ft.dropdown.Option("TERMINO_FIJO", "Término Fijo"),
                ft.dropdown.Option("PRESTACION_SERVICIOS", "Prestación de Servicios"),
                ft.dropdown.Option("APRENDIZAJE", "Aprendizaje"),
                ft.dropdown.Option("OTRO", "Otro"),
            ],
            dense=True
        )
        self.txt_salario_rango = ft.TextField(label="Rango Salarial (Ej: 1.5M - 2M COP)", dense=True)
        self.dp_fecha_cierre = ft.DatePicker(
            first_date=datetime.date.today(),
            on_change=self._on_date_change
        )
        self.btn_fecha_cierre = ft.OutlinedButton("Fecha de Cierre", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.page.open(self.dp_fecha_cierre))
        self.sw_activa = ft.Switch(label="Vacante Activa", value=True)

        self.btn_guardar = ft.ElevatedButton(text="Guardar Nueva Vacante", on_click=self._guardar_handler, icon=ft.icons.SAVE)
        self.btn_limpiar = ft.TextButton(text="Limpiar", on_click=self._limpiar_formulario, icon=ft.icons.CLEAR_ALL)

        # === LISTADO DE VACANTES ===
        self.txt_filtro_titulo = ft.TextField(label="Buscar por título...", on_submit=self._aplicar_filtros, dense=True, expand=True)
        self.btn_aplicar_filtros = ft.IconButton(icon=ft.icons.SEARCH, on_click=self._aplicar_filtros)
        self.paginacion_controls = ft.Row()

        self.tabla_vacantes = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Título")),
                ft.DataColumn(ft.Text("Empleador")),
                ft.DataColumn(ft.Text("Contrato")),
                ft.DataColumn(ft.Text("Activa")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        self.loading_tabla = ft.ProgressRing(visible=False)
        self.current_page = 1
        self.items_per_page = 10

    def did_mount(self):
        if self.dp_fecha_cierre not in self.page.overlay:
            self.page.overlay.append(self.dp_fecha_cierre)
            self.page.update()
        self._cargar_empresas_dropdown()
        self._cargar_listado_vacantes()

    def _aplicar_filtros(self, e):
        self.current_page = 1
        self._cargar_listado_vacantes()

    def _cargar_empresas_dropdown(self):
        # En la implementación real, esto cargaría las empresas del municipio del admin
        self.dd_empresa_asociada.options = [
            ft.dropdown.Option("1", "Hotel Jardín Mock"),
            ft.dropdown.Option("2", "Restaurante El Poblado Mock"),
        ]
        self.update()

    def _on_date_change(self, e):
        if e.control.value:
            self.btn_fecha_cierre.text = f"Cierre: {e.control.value.strftime('%Y-%m-%d')}"
        self.update()

    def _cargar_listado_vacantes(self):
        self.tabla_vacantes.rows.clear()
        self.loading_tabla.visible = True
        self.update()

        offset = (self.current_page - 1) * self.items_per_page
        filtros = {
            "codigo_municipio": self.codigo_municipio_admin,
            "titulo_vacante__icontains": self.txt_filtro_titulo.value or None
        }

        vacantes, total_items = db_manager.listar_vacantes_admin_paginado(
            filtros={k: v for k, v in filtros.items() if v is not None},
            orden={},
            limit=self.items_per_page,
            offset=offset
        )

        self.loading_tabla.visible = False
        if not vacantes:
            self.tabla_vacantes.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("No hay vacantes registradas para este municipio."), colspan=5)])
            )
        else:
            for vacante in vacantes:
                empleador = "N/A"
                if vacante.get("empresa_id"):
                    empleador = f"Empresa ID: {vacante.get('empresa_id')}"
                else:
                    empleador = vacante.get("nombre_empleador_alternativo", "N/A")

                self.tabla_vacantes.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(vacante.get("titulo_vacante"))),
                        ft.DataCell(ft.Text(empleador)),
                        ft.DataCell(ft.Text(vacante.get("tipo_contrato"))),
                        ft.DataCell(ft.Icon(ft.icons.CHECK if vacante.get("activa") else ft.icons.CLOSE)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar", data=vacante, on_click=self._cargar_para_edicion),
                        ])),
                    ])
                )

        self._actualizar_paginacion(total_items)
        self.update()

    def _guardar_handler(self, e):
        if not self.txt_titulo_vacante.value or not self.txt_descripcion.value:
            self.txt_titulo_vacante.error_text = "Campo obligatorio" if not self.txt_titulo_vacante.value else None
            self.txt_descripcion.error_text = "Campo obligatorio" if not self.txt_descripcion.value else None
            self.update()
            return

        datos = {
            "titulo_vacante": self.txt_titulo_vacante.value,
            "empresa_id": self.dd_empresa_asociada.value,
            "nombre_empleador_alternativo": self.txt_empleador_alternativo.value,
            "descripcion": self.txt_descripcion.value,
            "requisitos": self.txt_requisitos.value,
            "tipo_contrato": self.dd_tipo_contrato.value,
            "salario_rango": self.txt_salario_rango.value,
            "fecha_cierre": self.dp_fecha_cierre.value.isoformat() if self.dp_fecha_cierre.value else None,
            "activa": self.sw_activa.value,
            "codigo_municipio": self.codigo_municipio_admin,
            "publicada_por_usuario_id": self.user_id_admin
        }

        db_manager.crear_o_actualizar_vacante(datos, self.vacante_id_actual_edicion)

        self._limpiar_formulario()
        self._cargar_listado_vacantes()

    def _cargar_para_edicion(self, e):
        data = e.control.data
        self.vacante_id_actual_edicion = data.get("id_vacante")
        self.txt_titulo_vacante.value = data.get("titulo_vacante")
        self.dd_empresa_asociada.value = data.get("empresa_id")
        self.txt_empleador_alternativo.value = data.get("nombre_empleador_alternativo")
        self.txt_descripcion.value = data.get("descripcion")
        self.txt_requisitos.value = data.get("requisitos")
        self.dd_tipo_contrato.value = data.get("tipo_contrato")
        self.txt_salario_rango.value = data.get("salario_rango")
        if data.get("fecha_cierre"):
            self.dp_fecha_cierre.value = datetime.date.fromisoformat(data.get("fecha_cierre"))
            self.btn_fecha_cierre.text = f"Cierre: {self.dp_fecha_cierre.value.strftime('%Y-%m-%d')}"
        self.sw_activa.value = data.get("activa", True)
        self.btn_guardar.text = "Actualizar Vacante"
        self.update()

    def _limpiar_formulario(self, e=None):
        self.vacante_id_actual_edicion = None
        self.txt_titulo_vacante.value = ""
        self.dd_empresa_asociada.value = None
        self.txt_empleador_alternativo.value = ""
        self.txt_descripcion.value = ""
        self.txt_requisitos.value = ""
        self.dd_tipo_contrato.value = None
        self.txt_salario_rango.value = ""
        self.dp_fecha_cierre.value = None
        self.btn_fecha_cierre.text = "Fecha de Cierre"
        self.sw_activa.value = True
        self.txt_titulo_vacante.error_text = None
        self.btn_guardar.text = "Guardar Nueva Vacante"
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
        self._cargar_listado_vacantes()

    def build(self):
        formulario = ft.Container(
            content=ft.Column([
                ft.Text("Formulario de Vacante de Empleo", style=ft.TextThemeStyle.TITLE_LARGE),
                self.txt_titulo_vacante,
                self.dd_empresa_asociada,
                self.txt_empleador_alternativo,
                self.txt_descripcion,
                self.txt_requisitos,
                self.dd_tipo_contrato,
                self.txt_salario_rango,
                self.btn_fecha_cierre,
                self.sw_activa,
                ft.Row([self.btn_guardar, self.btn_limpiar], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=20
        )

        listado = ft.Column(
            controls=[
                ft.Text("Listado de Vacantes", style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Row([self.txt_filtro_titulo, self.btn_aplicar_filtros]),
                self.loading_tabla,
                self.tabla_vacantes,
                self.paginacion_controls
            ],
        )

        return ft.Column([
            ft.Text("Gestión de Vacantes de Empleo", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Formulario", icon=ft.icons.POST_ADD, content=formulario),
                    ft.Tab(text="Listado", icon=ft.icons.LIST_ALT, content=listado),
                ],
                expand=True
            )
        ])
