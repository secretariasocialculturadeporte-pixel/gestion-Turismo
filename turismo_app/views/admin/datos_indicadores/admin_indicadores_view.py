import flet as ft
from turismo_app.database import db_manager
import datetime

class AdminIndicadoresView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")

        # === FORMULARIO DE INDICADORES ===
        self.dd_tipo_indicador = ft.Dropdown(
            label="Tipo de Indicador*",
            options=[
                ft.dropdown.Option("OCUPACION_HOTELERA", "Ocupación Hotelera (%)"),
                ft.dropdown.Option("VISITANTES_EXCURSIONISTAS", "Visitantes Excursionistas (Día)"),
                ft.dropdown.Option("ECONOMIA_APORTE_PIB", "Aporte al PIB Local (%)"),
            ],
            dense=True
        )
        self.txt_valor_indicador = ft.TextField(label="Valor*", keyboard_type=ft.KeyboardType.NUMBER, dense=True)
        self.dp_fecha_medicion = ft.DatePicker(on_change=self._on_date_change)
        self.btn_fecha_medicion = ft.OutlinedButton("Fecha de Medición", on_click=lambda _: self.page.open(self.dp_fecha_medicion))
        self.txt_fuente_indicador = ft.TextField(label="Fuente del Dato", dense=True)

        self.btn_guardar = ft.ElevatedButton(text="Guardar Indicador", on_click=self._guardar_handler, icon=ft.icons.SAVE)

        # === LISTADO DE INDICADORES (Historial) ===
        self.tabla_indicadores = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tipo de Indicador")),
                ft.DataColumn(ft.Text("Valor")),
                ft.DataColumn(ft.Text("Fecha Medición")),
                ft.DataColumn(ft.Text("Fuente")),
            ],
            rows=[]
        )

    def did_mount(self):
        if self.dp_fecha_medicion not in self.page.overlay:
            self.page.overlay.append(self.dp_fecha_medicion)
            self.page.update()
        self._cargar_historial()

    def _on_date_change(self, e):
        if e.control.value:
            self.btn_fecha_medicion.text = f"Medición: {e.control.value.strftime('%Y-%m-%d')}"
        self.update()

    def _cargar_historial(self):
        self.tabla_indicadores.rows.clear()
        indicadores = db_manager.listar_indicadores(filtros={})

        if not indicadores:
            self.tabla_indicadores.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("No hay indicadores registrados."), colspan=4)])
            )
        else:
            for ind in indicadores:
                self.tabla_indicadores.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(ind.get("tipo_indicador"))),
                        ft.DataCell(ft.Text(str(ind.get("valor")))),
                        ft.DataCell(ft.Text(ind.get("fecha_medicion"))),
                        ft.DataCell(ft.Text(ind.get("fuente"))),
                    ])
                )
        self.update()

    def _guardar_handler(self, e):
        if not self.dd_tipo_indicador.value or not self.txt_valor_indicador.value:
            self.dd_tipo_indicador.error_text = "Obligatorio" if not self.dd_tipo_indicador.value else None
            self.txt_valor_indicador.error_text = "Obligatorio" if not self.txt_valor_indicador.value else None
            self.update()
            return

        datos = {
            "tipo_indicador": self.dd_tipo_indicador.value,
            "valor": self.txt_valor_indicador.value,
            "fecha_medicion": self.dp_fecha_medicion.value.isoformat() if self.dp_fecha_medicion.value else None,
            "fuente": self.txt_fuente_indicador.value,
            "codigo_municipio": self.codigo_municipio_admin
        }

        db_manager.guardar_indicador(datos)
        self._limpiar_formulario()
        self._cargar_historial()

    def _limpiar_formulario(self):
        self.dd_tipo_indicador.value = None
        self.txt_valor_indicador.value = ""
        self.dp_fecha_medicion.value = None
        self.btn_fecha_medicion.text = "Fecha de Medición"
        self.txt_fuente_indicador.value = ""
        self.update()

    def build(self):
        return ft.Column(
            [
                ft.Text("Registro de Indicadores Clave", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Container(
                    content=ft.Column([
                        self.dd_tipo_indicador,
                        self.txt_valor_indicador,
                        self.btn_fecha_medicion,
                        self.txt_fuente_indicador,
                        ft.Row([self.btn_guardar], alignment=ft.MainAxisAlignment.END)
                    ]),
                    padding=20,
                    border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                    border_radius=8
                ),
                ft.Divider(height=20),
                ft.Text("Historial de Indicadores Registrados", style=ft.TextThemeStyle.TITLE_LARGE),
                self.tabla_indicadores,
            ],
            spacing=15,
            scroll=ft.ScrollMode.ADAPTIVE,
            padding=20
        )
