import flet as ft
import math
from turismo_app.database import db_manager

TIPO_ATRACTIVO = "atractivos"
TIPO_EMPRESA = "empresas"

class CiudadanoTurismoView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        # ... (rest of the __init__ method from the last correct version)
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.spacing = 15
        self.padding = ft.padding.symmetric(vertical=10, horizontal=20)

        self.dialogo_detalle = ft.AlertDialog(modal=True, title=ft.Text("Detalle"))
        # Estado de la Paginación y Filtros
        self.current_page = {TIPO_ATRACTIVO: 1, TIPO_EMPRESA: 1}
        self.items_per_page = 10
        self.total_items = {TIPO_ATRACTIVO: 0, TIPO_EMPRESA: 0}

        # Controles
        self.dd_departamento_global = ft.Dropdown(label="Departamento", on_change=self._on_departamento_global_change)
        self.dd_municipio_global = ft.Dropdown(label="Municipio", on_change=self._on_municipio_global_change, disabled=True)
        self.loading_selector_muni = ft.ProgressRing(width=16, height=16, visible=False)
        self.txt_filtro_nombre_atractivo = ft.TextField(label="Buscar Atractivo")
        self.dd_filtro_tipo_categoria_atractivo = ft.Dropdown(label="Categoría")
        self.tabla_atractivos = ft.DataTable(columns=[ft.DataColumn(ft.Text("Nombre"))])
        self.pag_atractivos_controls_container = ft.Row()
        self.txt_filtro_nombre_empresa = ft.TextField(label="Buscar Empresa")
        self.dd_filtro_tipo_prestador_empresa = ft.Dropdown(label="Tipo")
        self.tabla_empresas = ft.DataTable(columns=[ft.DataColumn(ft.Text("Nombre"))])
        self.pag_empresas_controls_container = ft.Row()
        self.mensaje_general_vista = ft.Text("Seleccione un departamento y municipio...", visible=True)

        self.did_mount()

        # Construcción de la UI
        selectores_ubicacion = ft.Row([self.dd_departamento_global, self.dd_municipio_global, self.loading_selector_muni])
        seccion_atractivos_ui = ft.Column([self.txt_filtro_nombre_atractivo, self.tabla_atractivos, self.pag_atractivos_controls_container])
        seccion_empresas_ui = ft.Column([self.txt_filtro_nombre_empresa, self.tabla_empresas, self.pag_empresas_controls_container])

        self.controls = [
            ft.Text("Explora la Oferta Turística", size=28),
            selectores_ubicacion,
            ft.Divider(),
            self.mensaje_general_vista,
            ft.Tabs(
                tabs=[
                    ft.Tab(text="Atractivos", content=seccion_atractivos_ui),
                    ft.Tab(text="Empresas", content=seccion_empresas_ui),
                ],
                visible=not self.mensaje_general_vista.visible
            )
        ]

    def did_mount(self):
        self.page.dialog = self.dialogo_detalle
        self._cargar_departamentos_globales()
        # ... (resto de la lógica de did_mount)

    def _cargar_departamentos_globales(self):
        self.dd_departamento_global.options = [ft.dropdown.Option(d['codigo_departamento'], d['nombre_departamento']) for d in db_manager.obtener_departamentos()]
        self.update()

    # ... (resto de los métodos de la clase) ...
    def _on_departamento_global_change(self, e): pass
    def _on_municipio_global_change(self, e): pass
    def _cargar_listado_paginado_ciudadano(self, tipo_entidad: str): pass
    def _actualizar_controles_paginacion(self, tipo_entidad: str): pass
    def ver_detalle_atractivo(self, e): pass
    def ver_detalle_empresa(self, e): pass
