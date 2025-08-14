import flet as ft
from turismo_app.database import db_manager # Asegúrate que db_manager está completo
import datetime
import math

# --- IMPORTA TU CONSTANTE CAMPOS_PERCEPCION (si la tienes en un archivo separado) ---
# from ....core.mincit_definitions import CAMPOS_PERCEPCION
# SI NO, DEFINELA AQUÍ O ASEGÚRATE DE QUE LA CLASE ACCEDA A ELLA
# (La estructura de CAMPOS_PERCEPCION que usamos antes, con "label", "tipo", "min", "max", "options_dict", etc.)
CAMPOS_PERCEPCION = { # Ejemplo que usamos
    "volveria": {"label": "¿Volvería a visitar el destino?", "tipo": "switch"},
    "experiencia_general_positiva": {"label": "Experiencia General (1-Mala, 5-Excelente)", "tipo": "slider", "min":1, "max":5, "divisions":4, "default_value":3},
    # ... Añade TODOS tus campos de percepción
}


class _MockEventControl:
    def __init__(self, value=None): self.value = value
class _MockEvent:
    def __init__(self, control_value=None): self.control = _MockEventControl(control_value)


class AdminEncuestasView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.codigo_municipio_admin = page.session.get("user_codigo_municipio")
        self.user_id_admin = page.session.get("user_id")

        self.turista_registro_id_actual_edicion = None
        self.encuesta_percepcion_id_actual_edicion = None
        self.campos_formulario_percepcion_refs = {}

        # === PESTAÑA 1: Formulario de Encuesta ===
        # --- Parte A: Datos del Turista (`turistas_registros`) ---
        self.dp_fecha_encuesta = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime.now() + datetime.timedelta(days=1), # No permitir fechas futuras para la encuesta
            on_change=lambda e: self._actualizar_texto_fecha_picker(e, self.txt_fecha_encuesta_display, "Fecha Encuesta*")
        )
        self.btn_fecha_encuesta = ft.OutlinedButton("Fecha Encuesta*", icon=ft.icons.CALENDAR_TODAY_ROUNDED, on_click=lambda _: self.page.open(self.dp_fecha_encuesta))
        self.txt_fecha_encuesta_display = ft.Text(f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", style=ft.TextThemeStyle.BODY_LARGE)
        self.dp_fecha_encuesta.value = datetime.date.today() # Default a hoy

        self.txt_nombre_turista_opc = ft.TextField(label="Nombre Turista (Opcional)", dense=True, text_size=13)
        self.dd_genero_turista = ft.Dropdown(label="Género", options=[ft.dropdown.Option("","--"),ft.dropdown.Option("MASCULINO"), ft.dropdown.Option("FEMENINO"), ft.dropdown.Option("OTRO"), ft.dropdown.Option("PREFIERO_NO_DECIR")], dense=True, text_size=13)
        self.txt_edad_turista = ft.TextField(label="Edad", keyboard_type=ft.KeyboardType.NUMBER, width=100, dense=True, text_size=13)
        self.dd_rango_edad_turista = ft.Dropdown(label="Rango de Edad", options=[ # Cargar desde constantes o DB
            ft.dropdown.Option("","--"),ft.dropdown.Option("MENOR_18"), ft.dropdown.Option("18_25"), ft.dropdown.Option("26_35"),
            ft.dropdown.Option("36_45"), ft.dropdown.Option("46_55"), ft.dropdown.Option("56_65"), ft.dropdown.Option("MAYOR_65")
        ], dense=True, text_size=13)
        self.txt_nacionalidad_turista = ft.TextField(label="Nacionalidad Principal*", dense=True, text_size=13) # O Dropdown de países
        self.txt_pais_residencia_turista = ft.TextField(label="País Residencia (Si diferente, ISO2)", dense=True, text_size=13)

        self.dd_depto_origen_turista = ft.Dropdown(label="Dpto. Origen (Si Colombia)", on_change=self._cargar_municipios_origen_turista_form, options=[ft.dropdown.Option("","--Seleccione--")], dense=True, text_size=13)
        self.dd_municipio_origen_turista = ft.Dropdown(label="Mpio. Origen (Si Colombia)", disabled=True, options=[ft.dropdown.Option("","--Seleccione--")], dense=True, text_size=13)

        opciones_motivo_viaje = [ft.dropdown.Option("","--Seleccione--"), ft.dropdown.Option("OCIO_VACACIONES", "Ocio/Vacaciones"),
            ft.dropdown.Option("NEGOCIOS_TRABAJO", "Negocios/Trabajo"), ft.dropdown.Option("VISITA_FAMILIARES_AMIGOS", "Visita Familiares/Amigos"),
            # ... más opciones de la tabla `turistas_registros` ...
            ft.dropdown.Option("OTRO_MOTIVO", "Otro Motivo")
        ]
        self.dd_motivo_viaje_turista = ft.Dropdown(label="Motivo Principal Viaje*", options=opciones_motivo_viaje, on_change=self._toggle_otro_motivo_viaje_handler, dense=True, text_size=13)
        self.txt_otro_motivo_viaje_turista = ft.TextField(label="Especifique Otro Motivo", visible=False, dense=True, text_size=13)

        self.txt_num_acompanantes_adultos = ft.TextField(label="Nº Adultos Acompañantes", value="0")
        self.dp_llegada_turista = ft.DatePicker(on_change=lambda e: self._actualizar_fechas_y_noches_enc(e, "llegada"))
        self.btn_llegada_turista = ft.OutlinedButton("F. Llegada al Destino", on_click=lambda _:self.page.open(self.dp_llegada_turista))
        self.txt_llegada_turista_display = ft.Text("Llegada: (No sel.)")

        # --- Parte B: Percepción del Turista ---
        self.columna_campos_percepcion = self._crear_column_campos_percepcion_ui() # Genera los campos dinámicamente

        # --- Botones Formulario ---
        self.btn_guardar_encuesta = ft.ElevatedButton("Guardar Encuesta", icon=ft.icons.SAVE_ALL_OUTLINED, on_click=self._guardar_encuesta_handler, height=45)
        self.btn_limpiar_encuesta = ft.OutlinedButton("Limpiar Formulario", icon=ft.icons.CLEAR_ALL_SHARP, on_click=self._limpiar_formulario_encuesta_completo, height=45)

        self.dlg_confirmacion_encuesta = ft.AlertDialog(modal=True, title=ft.Text("Confirmar Encuesta"))


    def did_mount(self):
        if self.dp_fecha_encuesta not in self.page.overlay:
            self.page.overlay.append(self.dp_fecha_encuesta)
        if self.dp_llegada_turista not in self.page.overlay:
            self.page.overlay.append(self.dp_llegada_turista)
        self.page.update()
        self._cargar_listado_encuestas()

    def _cargar_listado_encuestas(self):
        # Placeholder - en una app real esto tendría filtros y paginación
        print("Cargando listado de encuestas (simulado)...")
        pass

    def _actualizar_texto_fecha_picker(self, e, text_control, label):
        if e.control.value:
            text_control.value = f"{label.replace('*', '')}: {e.control.value.strftime('%d/%m/%Y')}"
        else:
            text_control.value = f"{label.replace('*', '')}: (No sel.)"
        self.update()

    def _cargar_municipios_origen_turista_form(self, e):
        # Lógica para cargar municipios
        pass

    def _toggle_otro_motivo_viaje_handler(self, e):
        self.txt_otro_motivo_viaje_turista.visible = (e.control.value == "OTRO_MOTIVO")
        self.update()

    def _actualizar_fechas_y_noches_enc(self, e, tipo_fecha):
        # Lógica para calcular noches
        pass

    def _crear_column_campos_percepcion_ui(self):
        # Lógica para crear controles de percepción
        col = ft.Column()
        for key, config in CAMPOS_PERCEPCION.items():
            control = None
            if config['tipo'] == 'switch':
                control = ft.Switch(label=config['label'])
            elif config['tipo'] == 'slider':
                control = ft.Slider(min=config['min'], max=config['max'], divisions=config['divisions'], label=config['label'])
            if control:
                self.campos_formulario_percepcion_refs[key] = control
                col.controls.append(control)
        return col

    def _guardar_encuesta_handler(self, e):
        # Lógica de guardado simulado
        if not self.dp_fecha_encuesta.value or not self.txt_nacionalidad_turista.value:
            # Simple validación de ejemplo
            print("Error: Faltan campos obligatorios en la encuesta.")
            return

        datos_turista = {
            "fecha_encuesta": self.dp_fecha_encuesta.value.isoformat(),
            "nombre_turista": self.txt_nombre_turista_opc.value,
            "nacionalidad": self.txt_nacionalidad_turista.value,
            "codigo_municipio_encuestado": self.codigo_municipio_admin,
            "registrado_por_usuario_id": self.user_id_admin,
            # ... otros campos del turista
        }

        datos_percepcion = {}
        for key, control in self.campos_formulario_percepcion_refs.items():
            datos_percepcion[key] = control.value

        # En la vida real, esto podría ser una transacción o dos llamadas separadas
        # db_manager.guardar_registro_turista(datos_turista)
        # db_manager.guardar_percepcion(datos_percepcion)
        print("Guardando encuesta (simulado):", {"turista": datos_turista, "percepcion": datos_percepcion})

        self._limpiar_formulario_encuesta_completo()
        self._cargar_listado_encuestas()

    def _limpiar_formulario_encuesta_completo(self, e=None, reset_filtros_sa_no_usado=True):
        # Lógica de limpieza
        pass

    def build(self):
        return ft.Column([
            ft.Text("Vista de Encuestas Admin - TODO: Implementar UI completa con Tabs")
        ])
