import flet as ft
from turismo_app.database import db_manager
import datetime

# Lista de países para el dropdown
LISTA_PAISES = [
    "Colombia", "Estados Unidos", "España", "México", "Argentina", "Chile",
    "Perú", "Ecuador", "Venezuela", "Brasil", "Canadá", "Francia", "Alemania",
    "Italia", "Reino Unido", "Otro"
]

class EmpresaRegistroClientesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.fecha_seleccionada = datetime.date.today()

        # --- Controles ---
        self.dd_pais_origen = ft.Dropdown(
            label="País de Origen del Cliente*",
            options=[ft.dropdown.Option(pais) for pais in LISTA_PAISES]
        )
        self.txt_cantidad = ft.TextField(label="Cantidad de Clientes*", value="1", keyboard_type=ft.KeyboardType.NUMBER)

        self.dp_fecha_registro = ft.DatePicker(
            value=self.fecha_seleccionada,
            on_change=self._on_fecha_seleccionada,
        )
        self.btn_fecha_registro = ft.OutlinedButton(
            f"Fecha: {self.fecha_seleccionada.strftime('%Y-%m-%d')}",
            on_click=lambda _: self.page.open(self.dp_fecha_registro)
        )

        self.btn_registrar = ft.ElevatedButton("Registrar Clientes", on_click=self._registrar_handler)

        self.tabla_resumen = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("País de Origen")),
                ft.DataColumn(ft.Text("Total Clientes Registrados"), numeric=True),
            ]
        )

    def did_mount(self):
        if self.dp_fecha_registro not in self.page.overlay:
            self.page.overlay.append(self.dp_fecha_registro)
        self._cargar_resumen_clientes()

    def _on_fecha_seleccionada(self, e):
        self.fecha_seleccionada = self.dp_fecha_registro.value or datetime.date.today()
        self.btn_fecha_registro.text = f"Fecha: {self.fecha_seleccionada.strftime('%Y-%m-%d')}"
        self.page.update()

    def _cargar_resumen_clientes(self):
        resumen = db_manager.obtener_resumen_clientes_por_empresa(self.empresa_id)
        self.tabla_resumen.rows.clear()
        for row in resumen:
            self.tabla_resumen.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(row["pais_origen_cliente"])),
                    ft.DataCell(ft.Text(str(row["total_clientes"])))
                ])
            )
        self.page.update()

    def _registrar_handler(self, e):
        # Validación simple
        if not self.dd_pais_origen.value or not self.txt_cantidad.value:
            # Aquí se podría mostrar un snackbar de error
            return

        datos = {
            "empresa_id": self.empresa_id,
            "pais_origen_cliente": self.dd_pais_origen.value,
            "fecha_registro": self.fecha_seleccionada.isoformat(),
            "cantidad": int(self.txt_cantidad.value),
            "audit_user_id": self.page.session.get("user_id")
        }

        db_manager.registrar_cliente(datos)

        # Limpiar formulario y recargar el resumen
        self.dd_pais_origen.value = None
        self.txt_cantidad.value = "1"
        self._cargar_resumen_clientes()

    def build(self):
        self.did_mount()

        formulario = ft.Container(
            content=ft.Column([
                self.dd_pais_origen,
                self.txt_cantidad,
                self.btn_fecha_registro,
                self.btn_registrar
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            width=400,
        )

        resumen_container = ft.Column([
            ft.Text("Resumen de Clientes Registrados", style=ft.TextThemeStyle.TITLE_MEDIUM),
            self.tabla_resumen
        ])

        return ft.Column(
            expand=True,
            spacing=25,
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            controls=[
                ft.Text("Registro de Nacionalidad de Clientes", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("Esta herramienta ayuda a generar estadísticas sobre el origen de sus visitantes para la toma de decisiones."),
                ft.Row(
                    [
                        formulario,
                        ft.VerticalDivider(),
                        resumen_container,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=30
                )
            ]
        )
