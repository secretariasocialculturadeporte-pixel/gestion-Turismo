import flet as ft
from turismo_app.database import db_manager
import math

class ReportesMunicipioView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")

        # --- Controles para los KPIs y Gráficos ---
        self.kpi_total_atractivos = ft.Text("...", size=24, weight=ft.FontWeight.BOLD)
        self.kpi_total_empresas = ft.Text("...", size=24, weight=ft.FontWeight.BOLD)
        self.kpi_total_vacantes = ft.Text("...", size=24, weight=ft.FontWeight.BOLD)

        self.chart_empresas_por_tipo = ft.BarChart(
            bar_groups=[], # Se llenará dinámicamente
            border=ft.border.all(1, ft.colors.GREY_400),
            left_axis=ft.ChartAxis(
                labels_size=40, title="Número de Empresas", title_size=40
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label="Aloj. Urbano"),
                    ft.ChartAxisLabel(value=1, label="Aloj. Rural"),
                    ft.ChartAxisLabel(value=2, label="Rest./Bar"),
                ],
                labels_size=40,
                title="Tipo de Prestador",
                title_size=40,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=10, color=ft.colors.with_opacity(0.2, ft.colors.GREY_400)
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.WHITE),
            max_y=50, # Ajustar dinámicamente
            interactive=True,
            expand=True,
        )

    def did_mount(self):
        self._cargar_datos_reportes()

    def _cargar_datos_reportes(self):
        print(f"Cargando datos de reportes para el municipio: {self.codigo_municipio_admin}")

        # Llamada a la función simulada del db_manager
        stats = db_manager.obtener_stats_municipio(self.codigo_municipio_admin)

        kpis = stats.get("kpis", {})
        chart_data = stats.get("chart_empresas_por_tipo", {})

        self.kpi_total_atractivos.value = str(kpis.get("total_atractivos", 0))
        self.kpi_total_empresas.value = str(kpis.get("total_empresas", 0))
        self.kpi_total_vacantes.value = str(kpis.get("total_vacantes", 0))

        self.chart_empresas_por_tipo.bar_groups = [
            ft.BarChartGroup(x=0, bar_rods=[ft.BarChartRod(from_y=0, to_y=chart_data.get("ALOJAMIENTO_URBANO", 0), width=40, color=ft.colors.AMBER, tooltip="Aloj. Urbano")]),
            ft.BarChartGroup(x=1, bar_rods=[ft.BarChartRod(from_y=0, to_y=chart_data.get("ALOJAMIENTO_RURAL", 0), width=40, color=ft.colors.GREEN, tooltip="Aloj. Rural")]),
            ft.BarChartGroup(x=2, bar_rods=[ft.BarChartRod(from_y=0, to_y=chart_data.get("RESTAURANTE_BAR", 0), width=40, color=ft.colors.ORANGE, tooltip="Restaurantes/Bares")]),
        ]

        # Ajustar el eje Y del gráfico dinámicamente
        max_y_value = max(list(chart_data.values()) + [10]) # Asegurar un mínimo de 10
        self.chart_empresas_por_tipo.max_y = (math.ceil(max_y_value / 10) * 10) # Redondear al siguiente 10

        self.update()

    def _crear_kpi_card(self, titulo, control_valor, icono):
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Row([
                    ft.Icon(icono, size=30, opacity=0.8),
                    ft.Column([
                        ft.Text(titulo, size=16),
                        control_valor,
                    ])
                ])
            )
        )

    def build(self):
        kpi_row = ft.ResponsiveRow(
            controls=[
                ft.Column(col={"sm": 4}, controls=[self._crear_kpi_card("Total Atractivos", self.kpi_total_atractivos, ft.icons.PALETTE)]),
                ft.Column(col={"sm": 4}, controls=[self._crear_kpi_card("Total Empresas", self.kpi_total_empresas, ft.icons.BUSINESS)]),
                ft.Column(col={"sm": 4}, controls=[self._crear_kpi_card("Total Vacantes", self.kpi_total_vacantes, ft.icons.WORK)]),
            ]
        )

        chart_container = ft.Container(
            content=self.chart_empresas_por_tipo,
            padding=10,
            border_radius=8,
            expand=True,
        )

        return ft.Column(
            [
                ft.Text(f"Reportes del Municipio ({self.codigo_municipio_admin})", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Divider(),
                kpi_row,
                ft.Divider(),
                ft.Text("Empresas por Tipo de Prestador", style=ft.TextThemeStyle.TITLE_LARGE),
                chart_container,
            ],
            expand=True,
            spacing=20,
            scroll=ft.ScrollMode.ADAPTIVE
        )
