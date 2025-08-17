import flet as ft
from turismo_app.database import db_manager
import datetime
import math

class AdminAtractivosView:
    def __init__(self, page: ft.Page):
        self.page = page
        # ... (otros atributos iniciales)

        # --- Controles del Formulario ---
        self.txt_nombre_atractivo = ft.TextField(label="Nombre del Atractivo*", dense=True)
        # ... (otros campos)
        self.txt_latitud = ft.TextField(label="Latitud", keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_longitud = ft.TextField(label="Longitud", keyboard_type=ft.KeyboardType.NUMBER)

        self.btn_guardar = ft.ElevatedButton("Guardar", on_click=self._guardar_handler)
        # ... (otros botones)

    def _guardar_handler(self, e):
        if not self.txt_nombre_atractivo.value:
            # ... (validación básica)
            return

        datos = {
            "nombre_atractivo": self.txt_nombre_atractivo.value,
            # ... (otros campos)
            "latitud_grados_dec": float(self.txt_latitud.value) if self.txt_latitud.value else None,
            "longitud_grados_dec": float(self.txt_longitud.value) if self.txt_longitud.value else None,
            "audit_user_id": self.page.session.get("user_id")
        }

        db_manager.crear_o_actualizar_atractivo(datos, self.atractivo_id_actual_edicion)
        # ... (resto de la lógica de guardado)

    def _cargar_para_edicion(self, e):
        atractivo = e.control.data
        # ... (cargar otros campos)
        self.txt_latitud.value = str(atractivo.get("latitud_grados_dec", ""))
        self.txt_longitud.value = str(atractivo.get("longitud_grados_dec", ""))
        self.page.update()

    def build(self):
        # ... (construcción de la UI con los nuevos campos)
        formulario = ft.Column([
            # ... (controles existentes)
            ft.Row([self.txt_latitud, self.txt_longitud]),
            # ... (resto de controles)
        ])
        # ... (resto de la UI)
        return ft.Column() # Placeholder
