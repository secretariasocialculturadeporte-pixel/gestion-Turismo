import flet as ft
from turismo_app.database import db_manager
import datetime
import re
import math

class AdminEmpresasView:
    def __init__(self, page: ft.Page):
        self.page = page
        # ... (otros atributos iniciales)

        # --- Controles del Formulario ---
        self.txt_razon_social_emp = ft.TextField(label="Razón Social / Nombre Comercial*", dense=True)
        # ... (otros campos de texto)
        self.txt_latitud = ft.TextField(label="Latitud", keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_longitud = ft.TextField(label="Longitud", keyboard_type=ft.KeyboardType.NUMBER)

        self.btn_guardar_emp = ft.ElevatedButton(text="Guardar", on_click=self._guardar_empresa_handler)
        # ... (otros botones)

    def _guardar_empresa_handler(self, e):
        if not self._validar_formulario_empresa():
            return

        datos = {
            "razon_social_o_nombre_comercial": self.txt_razon_social_emp.value,
            # ... (otros campos)
            "latitud": float(self.txt_latitud.value) if self.txt_latitud.value else None,
            "longitud": float(self.txt_longitud.value) if self.txt_longitud.value else None,
            "audit_user_id": self.page.session.get("user_id")
        }

        db_manager.crear_o_actualizar_empresa(datos, self.empresa_id_actual_edicion)
        # ... (resto de la lógica de guardado)

    def _validar_formulario_empresa(self) -> bool:
        # ... (validaciones existentes)

        # Validación de Latitud y Longitud
        for control in [self.txt_latitud, self.txt_longitud]:
            if control.value:
                try:
                    float(control.value)
                except ValueError:
                    control.error_text = "Debe ser un número."
                    return False
        return True

    def _cargar_empresa_para_edicion(self, e):
        empresa = e.control.data
        # ... (cargar otros campos)
        self.txt_latitud.value = str(empresa.get("latitud", ""))
        self.txt_longitud.value = str(empresa.get("longitud", ""))
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
