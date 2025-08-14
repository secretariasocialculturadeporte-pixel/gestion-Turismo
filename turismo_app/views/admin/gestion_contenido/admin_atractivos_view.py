import flet as ft
from turismo_app.database import db_manager
import datetime

class AdminAtractivosView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")
        self.rol_admin = page.session.get("user_rol")
        self.atractivo_id_actual_edicion = None

        # --- Selector de Municipio para SuperAdmins (si aplica) ---
        self.dd_municipio_gestion_sa = ft.Dropdown(
            label="Gestionar Atractivos del Municipio",
            visible=(self.rol_admin == "SuperAdmin"),
            # Las opciones se cargarían en did_mount
        )

        # === FORMULARIO DE ATRACTIVO ===
        # NOTA: Estos son campos de ejemplo basados en el schema placeholder.
        # Se deben expandir para coincidir con el Formato Único de Inventarios del MinCIT.
        self.txt_nombre_atractivo = ft.TextField(label="Nombre del Atractivo*", dense=True)
        self.dd_tipo_categoria_principal = ft.Dropdown(
            label="Categoría Principal*",
            options=[
                ft.dropdown.Option("SITIOS_NATURALES", "Sitios Naturales"),
                ft.dropdown.Option("PATRIMONIO_CULTURAL_MATERIAL", "Patrimonio Cultural Material"),
                ft.dropdown.Option("PATRIMONIO_CULTURAL_INMATERIAL", "Patrimonio Cultural Inmaterial"),
                ft.dropdown.Option("FESTIVIDADES_EVENTOS", "Festividades y Eventos"),
            ],
            dense=True
        )
        self.txt_descripcion_breve = ft.TextField(label="Descripción Breve*", multiline=True, min_lines=3, dense=True)
        self.sw_aprobado_publicar = ft.Switch(label="Aprobar para Directorio Público", value=False)
        self.sw_activo = ft.Switch(label="Atractivo Activo", value=True)

        self.btn_guardar = ft.ElevatedButton(text="Guardar Nuevo Atractivo", on_click=self._guardar_handler, icon=ft.icons.SAVE)
        self.btn_limpiar = ft.TextButton(text="Limpiar", on_click=self._limpiar_formulario, icon=ft.icons.CLEAR_ALL)

        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Acción"),
            content=ft.Text("¿Está seguro de que desea eliminar este elemento?"),
            actions=[
                ft.TextButton("Sí", on_click=self._confirm_delete),
                ft.TextButton("No", on_click=self._close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # === LISTADO DE ATRACTIVOS ===
        self.tabla_atractivos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre del Atractivo")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Aprobado")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        self.loading_tabla = ft.ProgressRing(visible=False)

    def did_mount(self):
        # Lógica para cargar municipios si es SuperAdmin
        # Cargar el listado inicial
        self._cargar_listado_atractivos()

    def _cargar_listado_atractivos(self):
        self.tabla_atractivos.rows.clear()
        self.loading_tabla.visible = True
        self.update()

        filtros = {"codigo_municipio": self.codigo_municipio_admin}
        atractivos, _ = db_manager.listar_atractivos_admin_paginado(filtros=filtros, orden={}, limit=100, offset=0)

        self.loading_tabla.visible = False
        if not atractivos:
            self.tabla_atractivos.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("No hay atractivos registrados para este municipio."), colspan=5)])
            )
        else:
            for atractivo in atractivos:
                self.tabla_atractivos.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(atractivo.get("nombre_atractivo"))),
                        ft.DataCell(ft.Text(atractivo.get("tipo_categoria_principal"))),
                        ft.DataCell(ft.Icon(ft.icons.CHECK if atractivo.get("aprobado_publicar") else ft.icons.CLOSE, color=ft.colors.GREEN if atractivo.get("aprobado_publicar") else ft.colors.RED)),
                        ft.DataCell(ft.Icon(ft.icons.CHECK if atractivo.get("activo") else ft.icons.CLOSE, color=ft.colors.GREEN if atractivo.get("activo") else ft.colors.RED)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar", data=atractivo, on_click=self._cargar_para_edicion),
                            ft.IconButton(icon=ft.icons.DELETE, tooltip="Eliminar", data=atractivo.get("id_atractivo"), on_click=self._eliminar_handler),
                        ])),
                    ])
                )
        self.update()

    def _guardar_handler(self, e):
        if not self.txt_nombre_atractivo.value or not self.dd_tipo_categoria_principal.value:
            self.txt_nombre_atractivo.error_text = "Campo obligatorio" if not self.txt_nombre_atractivo.value else None
            self.dd_tipo_categoria_principal.error_text = "Campo obligatorio" if not self.dd_tipo_categoria_principal.value else None
            self.update()
            return

        datos = {
            "nombre_atractivo": self.txt_nombre_atractivo.value,
            "tipo_categoria_principal": self.dd_tipo_categoria_principal.value,
            "descripcion_breve": self.txt_descripcion_breve.value,
            "aprobado_publicar": self.sw_aprobado_publicar.value,
            "activo": self.sw_activo.value,
            "codigo_municipio": self.codigo_municipio_admin,
            "registrado_por_usuario_id": self.user_id_admin,
            "fecha_ultima_actualizacion": datetime.datetime.now().isoformat(),
        }

        db_manager.crear_o_actualizar_atractivo(datos, self.atractivo_id_actual_edicion)

        # Limpiar y recargar
        self._limpiar_formulario()
        self._cargar_listado_atractivos()

    def _cargar_para_edicion(self, e):
        atractivo_data = e.control.data
        self.atractivo_id_actual_edicion = atractivo_data.get("id_atractivo")
        self.txt_nombre_atractivo.value = atractivo_data.get("nombre_atractivo")
        self.dd_tipo_categoria_principal.value = atractivo_data.get("tipo_categoria_principal")
        self.txt_descripcion_breve.value = atractivo_data.get("descripcion_breve")
        self.sw_aprobado_publicar.value = atractivo_data.get("aprobado_publicar", False)
        self.sw_activo.value = atractivo_data.get("activo", True)
        self.btn_guardar.text = "Actualizar Atractivo"
        # En una app real, cambiaríamos a la pestaña del formulario
        self.update()

    def _eliminar_handler(self, e):
        # Guardar el ID para usarlo si el usuario confirma
        self.page.dialog = self.confirm_dialog
        self.confirm_dialog.data = e.control.data # Pasa el ID del atractivo al diálogo
        self.confirm_dialog.open = True
        self.page.update()

    def _confirm_delete(self, e):
        atractivo_id = self.confirm_dialog.data
        print(f"Simulando eliminación del atractivo ID: {atractivo_id}")
        # db_manager.eliminar_atractivo(atractivo_id) # Se necesitaría esta función
        self.confirm_dialog.open = False
        self._cargar_listado_atractivos()
        self.page.update()

    def _close_dialog(self, e):
        self.confirm_dialog.open = False
        self.page.update()

    def _limpiar_formulario(self, e=None):
        self.atractivo_id_actual_edicion = None
        self.txt_nombre_atractivo.value = ""
        self.dd_tipo_categoria_principal.value = None
        self.txt_descripcion_breve.value = ""
        self.sw_aprobado_publicar.value = False
        self.sw_activo.value = True
        self.txt_nombre_atractivo.error_text = None
        self.btn_guardar.text = "Guardar Nuevo Atractivo"
        self.update()

    def build(self):
        # Estructura de la vista con Pestañas
        formulario = ft.Container(
            content=ft.Column([
                ft.Text("Formulario de Atractivo Turístico", style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Text("NOTA: Este es un formulario simplificado. Se debe expandir según el Formato MinCIT."),
                self.txt_nombre_atractivo,
                self.dd_tipo_categoria_principal,
                self.txt_descripcion_breve,
                self.sw_aprobado_publicar,
                self.sw_activo,
                ft.Row([self.btn_guardar, self.btn_limpiar], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=20
        )

        listado = ft.Container(
            content=ft.Column([
                ft.Text("Listado de Atractivos", style=ft.TextThemeStyle.TITLE_LARGE),
                self.loading_tabla,
                self.tabla_atractivos
            ]),
            padding=20
        )

        return ft.Column([
            ft.Text("Gestión de Atractivos Turísticos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            self.dd_municipio_gestion_sa,
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Formulario", icon=ft.icons.EDIT_DOCUMENT, content=formulario),
                    ft.Tab(text="Listado", icon=ft.icons.LIST_ALT, content=listado),
                ],
                expand=True
            )
        ])
