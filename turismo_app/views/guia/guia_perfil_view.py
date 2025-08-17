import flet as ft
from turismo_app.database import db_manager

class GuiaPerfilView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.guia_id = page.session.get("user_id")

        # Controles del formulario
        self.txt_idiomas = ft.TextField(label="Idiomas (separados por coma)")
        self.txt_especialidades = ft.TextField(label="Especialidades (separadas por coma)")
        self.txt_certificaciones = ft.TextField(label="Certificaciones")
        self.txt_tarifa = ft.TextField(label="Tarifa por Hora (COP)", keyboard_type=ft.KeyboardType.NUMBER)
        self.btn_guardar_perfil = ft.ElevatedButton("Guardar Perfil", on_click=self._guardar_perfil_handler)

        # Controles de disponibilidad
        self.dp_disponibilidad = ft.DatePicker()
        self.btn_disponibilidad = ft.OutlinedButton("Gestionar Disponibilidad", on_click=lambda _: self.page.open(self.dp_disponibilidad))

    def _guardar_perfil_handler(self, e):
        datos = {
            "idiomas": self.txt_idiomas.value,
            "especialidades": self.txt_especialidades.value,
            "certificaciones": self.txt_certificaciones.value,
            "tarifa_por_hora": float(self.txt_tarifa.value),
            "audit_user_id": self.guia_id
        }
        db_manager.crear_o_actualizar_perfil_guia(datos, self.guia_id)
        self._cargar_perfil()

    def _cargar_perfil(self):
        perfil = db_manager.obtener_perfil_guia(self.guia_id)
        if perfil:
            self.txt_idiomas.value = perfil.get("idiomas", "")
            self.txt_especialidades.value = perfil.get("especialidades", "")
            self.txt_certificaciones.value = perfil.get("certificaciones", "")
            self.txt_tarifa.value = str(perfil.get("tarifa_por_hora", ""))
            self.page.update()

    def build(self):
        self._cargar_perfil()

        perfil_form = ft.Column([
            self.txt_idiomas,
            self.txt_especialidades,
            self.txt_certificaciones,
            self.txt_tarifa,
            self.btn_guardar_perfil,
        ])

        disponibilidad_section = ft.Column([
            ft.Text("Gestión de Disponibilidad", style=ft.TextThemeStyle.TITLE_MEDIUM),
            self.btn_disponibilidad,
        ])

        return ft.Column(
            [
                ft.Text("Mi Perfil de Guía", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                perfil_form,
                ft.Divider(),
                disponibilidad_section,
            ]
        )
