import flet as ft
from turismo_app.database import db_manager

class AdminEducacionTurismoView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")

        # === FORMULARIO ===
        self.txt_nombre_entidad = ft.TextField(label="Nombre de la Entidad Educativa*", dense=True)
        self.dd_nivel_educativo = ft.Dropdown(
            label="Nivel*",
            options=[
                ft.dropdown.Option("PRIMARIA"),
                ft.dropdown.Option("SECUNDARIA"),
                ft.dropdown.Option("TECNICA"),
                ft.dropdown.Option("UNIVERSITARIA"),
            ],
            dense=True
        )
        self.txt_programas_turismo = ft.TextField(label="Programas Relacionados con Turismo", multiline=True, dense=True)
        self.sw_colegio_amigo = ft.Switch(label="Es un Colegio Amigo del Turismo", value=False)

        self.btn_guardar = ft.ElevatedButton(text="Guardar Entidad", on_click=self._guardar_handler, icon=ft.icons.SAVE)
        self.btn_limpiar = ft.TextButton(text="Limpiar", on_click=self._limpiar_formulario)

        # === LISTADO ===
        self.tabla_entidades = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre de la Entidad")),
                ft.DataColumn(ft.Text("Nivel")),
                ft.DataColumn(ft.Text("Colegio Amigo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

    def did_mount(self):
        self._cargar_listado()

    def _cargar_listado(self):
        self.tabla_entidades.rows.clear()
        # En una app real, aquí habría filtros y paginación
        entidades = db_manager.listar_entidades_educativas(filtros={})

        if not entidades:
            self.tabla_entidades.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("No hay entidades registradas."), colspan=4)])
            )
        else:
            for entidad in entidades:
                self.tabla_entidades.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(entidad.get("nombre_entidad"))),
                        ft.DataCell(ft.Text(entidad.get("nivel"))),
                        ft.DataCell(ft.Icon(ft.icons.CHECK if entidad.get("colegio_amigo") else ft.icons.CLOSE)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar", data=entidad, on_click=self._cargar_para_edicion),
                        ])),
                    ])
                )
        self.update()

    def _guardar_handler(self, e):
        if not self.txt_nombre_entidad.value or not self.dd_nivel_educativo.value:
            self.txt_nombre_entidad.error_text = "Obligatorio"
            self.update()
            return

        datos = {
            "nombre_entidad": self.txt_nombre_entidad.value,
            "nivel": self.dd_nivel_educativo.value,
            "programas_turismo": self.txt_programas_turismo.value,
            "colegio_amigo": self.sw_colegio_amigo.value,
            "codigo_municipio": self.codigo_municipio_admin,
        }

        # db_manager.crear_o_actualizar_entidad_educativa(datos, self.entidad_id_actual_edicion)

        self._limpiar_formulario()
        self._cargar_listado()

    def _cargar_para_edicion(self, e):
        data = e.control.data
        # self.entidad_id_actual_edicion = data.get("id_entidad")
        self.txt_nombre_entidad.value = data.get("nombre_entidad")
        self.dd_nivel_educativo.value = data.get("nivel")
        self.txt_programas_turismo.value = data.get("programas_turismo")
        self.sw_colegio_amigo.value = data.get("colegio_amigo", False)
        self.update()

    def _limpiar_formulario(self, e=None):
        self.txt_nombre_entidad.value = ""
        self.dd_nivel_educativo.value = None
        self.txt_programas_turismo.value = ""
        self.sw_colegio_amigo.value = False
        self.update()

    def build(self):
        formulario = ft.Container(
            content=ft.Column([
                ft.Text("Formulario de Entidad Educativa", style=ft.TextThemeStyle.TITLE_LARGE),
                self.txt_nombre_entidad,
                self.dd_nivel_educativo,
                self.txt_programas_turismo,
                self.sw_colegio_amigo,
                ft.Row([self.btn_guardar, self.btn_limpiar], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=20
        )

        listado = ft.Container(
            content=ft.Column([
                ft.Text("Listado de Entidades", style=ft.TextThemeStyle.TITLE_LARGE),
                self.tabla_entidades
            ]),
            padding=20
        )

        return ft.Column([
            ft.Text("Gestión de Entidades Educativas y Colegios Amigos del Turismo", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Formulario", icon=ft.icons.SCHOOL, content=formulario),
                    ft.Tab(text="Listado", icon=ft.icons.LIST, content=listado),
                ],
                expand=True
            )
        ])
