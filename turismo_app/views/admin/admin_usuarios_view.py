import flet as ft
from turismo_app.database import db_manager
import datetime

class AdminUsuariosView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.current_user_role = page.session.get("user_rol")
        self.user_id_actual_edicion = None

        # === FORMULARIO DE USUARIO ===
        self.txt_nombre_usuario = ft.TextField(label="Nombre de Usuario*", dense=True)
        self.txt_nombre_completo = ft.TextField(label="Nombre Completo*", dense=True)
        self.txt_email = ft.TextField(label="Email*", keyboard_type=ft.KeyboardType.EMAIL, dense=True)
        self.txt_password = ft.TextField(label="Contraseña (dejar en blanco para no cambiar)", password=True, can_reveal_password=True, dense=True)

        # Las opciones de rol podrían depender del rol del admin actual
        self.dd_rol = ft.Dropdown(
            label="Rol*",
            options=[
                ft.dropdown.Option("AdminMunicipal", "Admin Municipal"),
                ft.dropdown.Option("Ciudadano", "Ciudadano"),
            ],
            dense=True
        )
        self.dd_municipio_asignado = ft.Dropdown(label="Municipio Asignado (para Admins)", dense=True) # Poblar desde DB
        self.sw_activo = ft.Switch(label="Usuario Activo", value=True)

        self.btn_guardar = ft.ElevatedButton(text="Guardar Nuevo Usuario", on_click=self._guardar_handler, icon=ft.icons.SAVE)
        self.btn_limpiar = ft.TextButton(text="Limpiar", on_click=self._limpiar_formulario, icon=ft.icons.CLEAR_ALL)

        # === LISTADO DE USUARIOS ===
        self.txt_filtro_nombre = ft.TextField(label="Buscar por nombre...", on_submit=self._aplicar_filtros, dense=True, expand=True)
        self.btn_aplicar_filtros = ft.IconButton(icon=ft.icons.SEARCH, on_click=self._aplicar_filtros)
        self.paginacion_controls = ft.Row()

        self.tabla_usuarios = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre de Usuario")),
                ft.DataColumn(ft.Text("Nombre Completo")),
                ft.DataColumn(ft.Text("Rol")),
                ft.DataColumn(ft.Text("Municipio")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        self.loading_tabla = ft.ProgressRing(visible=False)
        self.current_page = 1
        self.items_per_page = 10

    def did_mount(self):
        # Cargar municipios para el dropdown
        self._cargar_listado_usuarios()

    def _aplicar_filtros(self, e):
        self.current_page = 1
        self._cargar_listado_usuarios()

    def _cargar_listado_usuarios(self):
        self.tabla_usuarios.rows.clear()
        self.loading_tabla.visible = True
        self.update()

        # En una implementación real, el db_manager debería manejar paginación y filtros
        # Aquí lo simulamos sobre la lista completa
        all_users = db_manager.listar_usuarios_admin(filtros={})

        # Simulación de filtro
        if self.txt_filtro_nombre.value:
            term = self.txt_filtro_nombre.value.lower()
            all_users = [u for u in all_users if term in u.get("nombre_completo", "").lower() or term in u.get("nombre_usuario", "").lower()]

        total_items = len(all_users)
        offset = (self.current_page - 1) * self.items_per_page
        paginated_users = all_users[offset : offset + self.items_per_page]

        self.loading_tabla.visible = False
        if not paginated_users:
            self.tabla_usuarios.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("No se encontraron usuarios."), colspan=6)])
            )
        else:
            for usuario in paginated_users:
                self.tabla_usuarios.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(usuario.get("nombre_usuario"))),
                        ft.DataCell(ft.Text(usuario.get("nombre_completo"))),
                        ft.DataCell(ft.Text(usuario.get("rol"))),
                        ft.DataCell(ft.Text(usuario.get("codigo_municipio", "N/A"))),
                        ft.DataCell(ft.Icon(ft.icons.CHECK if usuario.get("activo") else ft.icons.CLOSE)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar", data=usuario, on_click=self._cargar_para_edicion),
                        ])),
                    ])
                )

        self._actualizar_paginacion(total_items)
        self.update()

    def _guardar_handler(self, e):
        if not self.txt_nombre_usuario.value or not self.txt_email.value or not self.dd_rol.value:
            # Simple validation
            self.txt_nombre_usuario.error_text = "Obligatorio" if not self.txt_nombre_usuario.value else None
            self.txt_email.error_text = "Obligatorio" if not self.txt_email.value else None
            self.dd_rol.error_text = "Obligatorio" if not self.dd_rol.value else None
            self.update()
            return

        datos = {
            "nombre_usuario": self.txt_nombre_usuario.value,
            "nombre_completo": self.txt_nombre_completo.value,
            "email": self.txt_email.value,
            "rol": self.dd_rol.value,
            "codigo_municipio": self.dd_municipio_asignado.value,
            "activo": self.sw_activo.value,
        }
        if self.txt_password.value:
            datos["password"] = self.txt_password.value

        db_manager.crear_o_actualizar_usuario(datos, self.user_id_actual_edicion)

        self._limpiar_formulario()
        self._cargar_listado_usuarios()

    def _cargar_para_edicion(self, e):
        data = e.control.data
        self.user_id_actual_edicion = data.get("id_usuario")
        self.txt_nombre_usuario.value = data.get("nombre_usuario")
        self.txt_nombre_completo.value = data.get("nombre_completo")
        self.txt_email.value = data.get("email")
        self.dd_rol.value = data.get("rol")
        self.dd_municipio_asignado.value = data.get("codigo_municipio")
        self.sw_activo.value = data.get("activo", True)
        self.txt_password.value = ""
        self.btn_guardar.text = "Actualizar Usuario"
        self.update()

    def _limpiar_formulario(self, e=None):
        self.user_id_actual_edicion = None
        self.txt_nombre_usuario.value = ""
        self.txt_nombre_completo.value = ""
        self.txt_email.value = ""
        self.txt_password.value = ""
        self.dd_rol.value = None
        self.dd_municipio_asignado.value = None
        self.sw_activo.value = True
        self.txt_nombre_usuario.error_text = None
        self.txt_email.error_text = None
        self.btn_guardar.text = "Guardar Nuevo Usuario"
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
        self._cargar_listado_usuarios()

    def build(self):
        # Solo SuperAdmins pueden ver esta vista
        if self.current_user_role != "SuperAdmin":
            return ft.Container(
                content=ft.Text("Acceso denegado. Se requiere rol de SuperAdmin.", color=ft.colors.ERROR),
                padding=50
            )

        formulario = ft.Container(
            content=ft.Column([
                ft.Text("Formulario de Usuario", style=ft.TextThemeStyle.TITLE_LARGE),
                self.txt_nombre_usuario,
                self.txt_nombre_completo,
                self.txt_email,
                self.txt_password,
                self.dd_rol,
                self.dd_municipio_asignado,
                self.sw_activo,
                ft.Row([self.btn_guardar, self.btn_limpiar], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=20
        )

        listado = ft.Column(
            [
                ft.Text("Listado de Usuarios", style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Row([self.txt_filtro_nombre, self.btn_aplicar_filtros]),
                self.loading_tabla,
                self.tabla_usuarios,
                self.paginacion_controls,
            ]
        )

        return ft.Column([
            ft.Text("Gestión de Usuarios del Sistema", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Formulario", icon=ft.icons.PERSON_ADD, content=formulario),
                    ft.Tab(text="Listado", icon=ft.icons.LIST_ALT, content=listado),
                ],
                expand=True
            )
        ])
