import flet as ft
from turismo_app.database import db_manager
import datetime

class AdminDiagnosticoTerritorialView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")

        # === FORMULARIO DE DIAGNÓSTICO ===
        # NOTA: Este es un formulario de ejemplo. La versión real debería
        # generarse dinámicamente a partir de METODOLOGIA_MINCIT_NDTT_REAL
        # en mincit_definitions.py

        self.txt_anio_diagnostico = ft.TextField(label="Año del Diagnóstico*", keyboard_type=ft.KeyboardType.NUMBER, dense=True)

        # Ejemplo de una dimensión
        self.sl_infraestructura = ft.Slider(min=0, max=100, divisions=20, label="1. Infraestructura y Conectividad ({value})")
        self.txt_infraestructura_obs = ft.TextField(label="Obs. Infraestructura", dense=True)

        # Ejemplo de otra dimensión
        self.sl_sostenibilidad = ft.Slider(min=0, max=100, divisions=20, label="2. Sostenibilidad Ambiental ({value})")
        self.txt_sostenibilidad_obs = ft.TextField(label="Obs. Sostenibilidad", dense=True)

        # Ejemplo de otra dimensión
        self.sl_gestion_destino = ft.Slider(min=0, max=100, divisions=20, label="3. Gestión del Destino ({value})")
        self.txt_gestion_destino_obs = ft.TextField(label="Obs. Gestión", dense=True)

        self.txt_resultado_total = ft.TextField(label="Resultado Total (Calculado)", read_only=True, dense=True)

        self.btn_guardar = ft.ElevatedButton(text="Guardar Diagnóstico", on_click=self._guardar_handler, icon=ft.icons.SAVE)
        self.btn_cargar_ultimo = ft.TextButton(text="Cargar Último Diagnóstico", on_click=self._cargar_ultimo_handler)

    def did_mount(self):
        self._cargar_ultimo_handler()

    def _cargar_ultimo_handler(self, e=None):
        print(f"Cargando último diagnóstico para el municipio: {self.codigo_municipio_admin}")
        diagnostico = db_manager.obtener_ultimo_diagnostico(self.codigo_municipio_admin)
        if diagnostico:
            self.txt_anio_diagnostico.value = diagnostico.get("anio_diagnostico", "")
            self.sl_infraestructura.value = diagnostico.get("dim_infraestructura", 0)
            self.txt_infraestructura_obs.value = diagnostico.get("obs_infraestructura", "")
            self.sl_sostenibilidad.value = diagnostico.get("dim_sostenibilidad", 0)
            self.txt_sostenibilidad_obs.value = diagnostico.get("obs_sostenibilidad", "")
            self.sl_gestion_destino.value = diagnostico.get("dim_gestion_destino", 0)
            self.txt_gestion_destino_obs.value = diagnostico.get("obs_gestion_destino", "")
            self.txt_resultado_total.value = str(diagnostico.get("resultado_total", ""))
        else:
            self.txt_anio_diagnostico.value = str(datetime.date.today().year)
            self.sl_infraestructura.value = 0
            self.txt_infraestructura_obs.value = ""
            self.sl_sostenibilidad.value = 0
            self.txt_sostenibilidad_obs.value = ""
            self.sl_gestion_destino.value = 0
            self.txt_gestion_destino_obs.value = ""
            self.txt_resultado_total.value = "N/A"
        self.update()

    def _guardar_handler(self, e):
        if not self.txt_anio_diagnostico.value:
            self.txt_anio_diagnostico.error_text = "El año es obligatorio"
            self.update()
            return

        datos = {
            "codigo_municipio": self.codigo_municipio_admin,
            "anio_diagnostico": int(self.txt_anio_diagnostico.value),
            "dim_infraestructura": self.sl_infraestructura.value,
            "obs_infraestructura": self.txt_infraestructura_obs.value,
            "dim_sostenibilidad": self.sl_sostenibilidad.value,
            "obs_sostenibilidad": self.txt_sostenibilidad_obs.value,
            "dim_gestion_destino": self.sl_gestion_destino.value,
            "obs_gestion_destino": self.txt_gestion_destino_obs.value,
            "resultado_total": (self.sl_infraestructura.value + self.sl_sostenibilidad.value + self.sl_gestion_destino.value) / 3,
            "registrado_por_usuario_id": self.user_id_admin,
            "fecha_registro": datetime.datetime.now().isoformat()
        }

        db_manager.guardar_diagnostico(datos)
        print("Diagnóstico guardado (simulado).")
        self._cargar_ultimo_handler()

    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Registro de Diagnóstico Territorial", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    ft.Text("NOTA: Formulario simplificado. La versión final debe reflejar la metodología MinCIT completa.", italic=True),
                    ft.Divider(),
                    self.txt_anio_diagnostico,
                    ft.Text("Dimensión: Infraestructura y Conectividad", weight=ft.FontWeight.BOLD),
                    self.sl_infraestructura,
                    self.txt_infraestructura_obs,
                    ft.Text("Dimensión: Sostenibilidad Ambiental", weight=ft.FontWeight.BOLD),
                    self.sl_sostenibilidad,
                    self.txt_sostenibilidad_obs,
                    ft.Text("Dimensión: Gestión del Destino", weight=ft.FontWeight.BOLD),
                    self.sl_gestion_destino,
                    self.txt_gestion_destino_obs,
                    ft.Divider(),
                    self.txt_resultado_total,
                    ft.Row([self.btn_guardar, self.btn_cargar_ultimo], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=10,
                scroll=ft.ScrollMode.ADAPTIVE,
            ),
            padding=20
        )
