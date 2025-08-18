import flet as ft
from turismo_app.database import db_manager
import datetime

class CalendarioDisponibilidadView:
    def __init__(self, page: ft.Page, empresa_id: int):
        self.page = page
        self.empresa_id = empresa_id

        # Controles
        self.dd_tipo_recurso = ft.Dropdown(label="Filtrar por Tipo de Recurso")
        self.calendario_grid = ft.GridView(
            expand=True,
            runs_count=7, # 7 días de la semana
            max_extent=100,
            child_aspect_ratio=1.0,
        )

    def build(self):
        # Lógica para cargar los tipos de recursos de la empresa
        # y generar el calendario

        return ft.Column(
            [
                ft.Text("Calendario de Disponibilidad", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                self.dd_tipo_recurso,
                ft.Divider(),
                self.calendario_grid,
            ],
            expand=True
        )
