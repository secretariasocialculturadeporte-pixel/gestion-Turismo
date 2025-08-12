import flet as ft
from turismo_app.database import db_manager
import datetime

# Asumimos una ruta a la que volver
ROUTE_HOME_CIUDADANO = "/"

class CiudadanoFeedbackView(ft.UserControl):
    def __init__(self, page: ft.Page, municipio_codigo_param: str | None = None, atractivo_id_param: str | None = None):
        super().__init__()
        self.page = page
        self.user_id_actual = self.page.session.get("user_id")
        self.municipio_codigo_param = municipio_codigo_param
        self.atractivo_id_param = atractivo_id_param

        self.selected_depto_feedback = None
        self.selected_municipio_feedback = None
        self.valoracion_destino_general_id_actual = None
        self.atractivos_visitados_para_valorar = []

        # --- Controles ---
        # Selección de municipio a valorar
        self.dd_departamento_feedback = ft.Dropdown(label="Departamento que visitaste*", on_change=self._on_depto_feedback_change)
        self.dd_municipio_feedback = ft.Dropdown(label="Municipio que visitaste*", on_change=self._on_municipio_feedback_change, disabled=True)

        # Formulario de valoración general
        self.txt_nombre_visitante_opc = ft.TextField(label="Tu nombre (Opcional, si no has iniciado sesión)", visible=not self.user_id_actual)
        self.txt_email_visitante_opc = ft.TextField(label="Tu email (Opcional, para contacto)", visible=not self.user_id_actual)
        self.sl_calificacion_general_destino = ft.Slider(min=1, max=5, divisions=4, label="Calificación General: {value} estrellas")
        self.txt_comentario_general_destino = ft.TextField(label="Comentarios generales sobre el destino", multiline=True, min_lines=3)
        self.txt_aspectos_positivos_destino = ft.TextField(label="¿Qué fue lo que más te gustó?", multiline=True)
        self.txt_aspectos_a_mejorar_destino = ft.TextField(label="¿Qué crees que podría mejorar?", multiline=True)
        self.dd_probabilidad_volver_destino = ft.Dropdown(label="¿Qué tan probable es que vuelvas?", options=self._crear_opciones_escala(1, 10))
        self.dd_probabilidad_recomendar_destino = ft.Dropdown(label="¿Qué tan probable es que lo recomiendes?", options=self._crear_opciones_escala(1, 10))
        self.btn_guardar_valoracion_general = ft.ElevatedButton("Guardar Valoración del Destino", icon=ft.icons.SAVE, on_click=self._guardar_valoracion_general_handler, disabled=True)

        # Sección para valorar atractivos específicos
        self.dd_atractivos_del_municipio_para_valorar = ft.Dropdown(label="Selecciona un atractivo que visitaste para añadirlo a la lista", on_change=self._seleccionar_atractivo_para_valorar)
        self.lista_atractivos_a_valorar_ui = ft.Column()
        self.seccion_valorar_atractivos = ft.Column(
            [
                ft.Divider(),
                ft.Text("Valora los Atractivos que Visitaste", style=ft.TextThemeStyle.TITLE_MEDIUM),
                self.dd_atractivos_del_municipio_para_valorar,
                self.lista_atractivos_a_valorar_ui
            ],
            visible=False
        )

        self.btn_finalizar_feedback_completo = ft.FilledButton("Finalizar y Enviar Todas las Valoraciones", icon=ft.icons.SEND_ROUNDED, on_click=self._finalizar_y_enviar_todo, visible=False)

    def _crear_opciones_escala(self, min_val, max_val):
        return [ft.dropdown.Option(str(i), str(i)) for i in range(min_val, max_val + 1)]

    def did_mount(self):
        self._cargar_departamentos_feedback()
        # Lógica para pre-seleccionar si vienen parámetros
        if self.municipio_codigo_param:
            muni_info = db_manager.obtener_municipio_por_codigo(self.municipio_codigo_param)
            if muni_info:
                self.dd_departamento_feedback.value = muni_info['codigo_departamento']
                self._cargar_municipios_feedback(muni_info['codigo_departamento'], self.municipio_codigo_param)

    def _cargar_departamentos_feedback(self):
        self.dd_departamento_feedback.options = [ft.dropdown.Option(d['codigo_departamento'], d['nombre_departamento']) for d in db_manager.obtener_departamentos()]
        self.update()

    def _on_depto_feedback_change(self, e):
        self.selected_depto_feedback = e.control.value
        self.dd_municipio_feedback.disabled = True
        self.dd_municipio_feedback.value = None
        self.update()
        self._cargar_municipios_feedback(self.selected_depto_feedback)

    def _cargar_municipios_feedback(self, depto_code, default_muni=None):
        self.dd_municipio_feedback.options = [ft.dropdown.Option(m['codigo_municipio'], m['nombre_municipio']) for m in db_manager.obtener_municipios_por_departamento(depto_code)]
        self.dd_municipio_feedback.disabled = False
        if default_muni:
            self.dd_municipio_feedback.value = default_muni
            self._on_municipio_feedback_change(None)
        self.update()

    def _on_municipio_feedback_change(self, e):
        self.selected_municipio_feedback = self.dd_municipio_feedback.value
        self.btn_guardar_valoracion_general.disabled = not bool(self.selected_municipio_feedback)
        # Limpiar valoraciones previas si cambia de municipio
        self.limpiar_formulario_valoracion_general()
        self.update()

    def _guardar_valoracion_general_handler(self, e):
        datos = self._recoger_datos_valoracion_general()
        if not datos: return

        self.valoracion_destino_general_id_actual = db_manager.crear_valoracion_destino(datos)
        if self.valoracion_destino_general_id_actual:
            self.btn_guardar_valoracion_general.text = "Valoración General Guardada ✓"
            self.btn_guardar_valoracion_general.disabled = True
            self.btn_guardar_valoracion_general.icon = ft.icons.CHECK_CIRCLE_OUTLINE
            self.seccion_valorar_atractivos.visible = True
            self.btn_finalizar_feedback_completo.visible = True
            self._mostrar_snackbar("Valoración del destino guardada. Ahora puedes valorar atractivos específicos o finalizar.", False)
            self._cargar_atractivos_para_valorar_dropdown(self.selected_municipio_feedback)
        else:
            self._mostrar_snackbar("Error al guardar la valoración del destino.", True)
        self.update()

    def _cargar_atractivos_para_valorar_dropdown(self, muni_code):
        # Esta función debería obtener los atractivos del municipio
        # Mock:
        self.dd_atractivos_del_municipio_para_valorar.options = [
            ft.dropdown.Option("1", "Atractivo Falso 1"),
            ft.dropdown.Option("2", "Atractivo Falso 2"),
        ]
        self.update()

    def _seleccionar_atractivo_para_valorar(self, e):
        atractivo_id_sel = self.dd_atractivos_del_municipio_para_valorar.value
        if not atractivo_id_sel: return

        if any(item["atractivo_id"] == int(atractivo_id_sel) for item in self.atractivos_visitados_para_valorar):
            self._mostrar_snackbar("Este atractivo ya fue añadido.", is_error=False)
            return

        atractivo_info = db_manager.obtener_atractivo_por_id(int(atractivo_id_sel))
        if not atractivo_info: return

        calificacion_control = ft.Slider(min=1, max=5, divisions=4, label="Calificación: {value} estrellas")
        comentario_control = ft.TextField(label=f"Comentarios sobre {atractivo_info.get('nombre_atractivo')}", multiline=True)

        nuevo_atractivo_data = {
            "atractivo_id": int(atractivo_id_sel),
            "nombre_atractivo": atractivo_info.get('nombre_atractivo'),
            "calificacion_control": calificacion_control,
            "comentario_control": comentario_control
        }
        self.atractivos_visitados_para_valorar.append(nuevo_atractivo_data)

        self.lista_atractivos_a_valorar_ui.controls.append(
            ft.Card(
                content=ft.Container(
                    ft.Column([
                        ft.Text(atractivo_info.get('nombre_atractivo'), style=ft.TextThemeStyle.TITLE_MEDIUM),
                        calificacion_control,
                        comentario_control
                    ]),
                    padding=10
                )
            )
        )
        self.dd_atractivos_del_municipio_para_valorar.value = None
        self.update()

    def _finalizar_y_enviar_todo(self, e):
        num_atr_guardados_exito = 0
        for item_atr_val in self.atractivos_visitados_para_valorar:
            datos_val_atr = {
                "valoracion_destino_id": self.valoracion_destino_general_id_actual,
                "atractivo_id": item_atr_val["atractivo_id"],
                "calificacion_atractivo": int(item_atr_val["calificacion_control"].value),
                "comentario_atractivo": item_atr_val["comentario_control"].value or None,
                # ... otros datos ...
            }
            if db_manager.crear_valoracion_atractivo(datos_val_atr):
                num_atr_guardados_exito += 1

        self._mostrar_snackbar(f"¡Gracias por tu feedback! Se guardaron {num_atr_guardados_exito} valoraciones.", False, 5000)
        self.limpiar_todo_feedback_view()
        self.page.go(ROUTE_HOME_CIUDADANO)

    def limpiar_formulario_valoracion_general(self):
        self.sl_calificacion_general_destino.value = 3
        self.txt_comentario_general_destino.value = ""
        # ... limpiar todos los campos ...
        self.update()

    def limpiar_todo_feedback_view(self):
        self.limpiar_formulario_valoracion_general()
        self.atractivos_visitados_para_valorar.clear()
        self.lista_atractivos_a_valorar_ui.controls.clear()
        self.seccion_valorar_atractivos.visible = False
        self.btn_finalizar_feedback_completo.visible = False
        self.btn_guardar_valoracion_general.disabled = False
        self.btn_guardar_valoracion_general.text = "Guardar Valoración del Destino"
        self.btn_guardar_valoracion_general.icon = ft.icons.SAVE
        self.dd_departamento_feedback.value = None
        self.dd_municipio_feedback.value = None
        self.dd_municipio_feedback.disabled = True
        self.update()

    def _recoger_datos_valoracion_general(self):
        return {
            "codigo_municipio_evaluado": self.selected_municipio_feedback,
            "usuario_id": self.user_id_actual,
            "nombre_visitante_anonimo": self.txt_nombre_visitante_opc.value or None,
            "email_contacto_opcional": self.txt_email_visitante_opc.value or None,
            "calificacion_general_destino": int(self.sl_calificacion_general_destino.value),
            "comentario_general_destino": self.txt_comentario_general_destino.value or None,
            "aspectos_positivos_destino": self.txt_aspectos_positivos_destino.value or None,
            "aspectos_a_mejorar_destino": self.txt_aspectos_a_mejorar_destino.value or None,
            "probabilidad_volver": int(self.dd_probabilidad_volver_destino.value) if self.dd_probabilidad_volver_destino.value else None,
            "probabilidad_recomendar": int(self.dd_probabilidad_recomendar_destino.value) if self.dd_probabilidad_recomendar_destino.value else None,
            "fecha_valoracion": datetime.datetime.now().isoformat(timespec='seconds'),
        }

    def _mostrar_snackbar(self, msg, is_error=False, length=3000):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg),
            bgcolor=ft.colors.ERROR if is_error else ft.colors.GREEN_700,
            duration=length
        )
        self.page.snack_bar.open = True
        self.page.update()

    def build(self):
        return ft.Column(
            [
                ft.Text("Comparte tu Experiencia", style=ft.TextThemeStyle.HEADLINE_MEDIUM, text_align=ft.TextAlign.CENTER),
                ft.Text("Tu opinión es fundamental para mejorar nuestros destinos turísticos."),
                ft.ResponsiveRow(
                    [
                        ft.Column([self.dd_departamento_feedback], col={"sm":12, "md":6}),
                        ft.Column([self.dd_municipio_feedback], col={"sm":12, "md":6}),
                    ]
                ),
                ft.Divider(),
                ft.Text("Valoración General del Destino", style=ft.TextThemeStyle.TITLE_LARGE),
                self.sl_calificacion_general_destino,
                self.txt_comentario_general_destino,
                self.txt_aspectos_positivos_destino,
                self.txt_aspectos_a_mejorar_destino,
                ft.ResponsiveRow(
                    [
                        ft.Column([self.dd_probabilidad_volver_destino], col={"sm":12, "md":6}),
                        ft.Column([self.dd_probabilidad_recomendar_destino], col={"sm":12, "md":6}),
                    ]
                ),
                ft.Row([self.btn_guardar_valoracion_general], alignment=ft.MainAxisAlignment.CENTER),
                self.seccion_valorar_atractivos,
                ft.Row([self.btn_finalizar_feedback_completo], alignment=ft.MainAxisAlignment.CENTER, visible=self.btn_finalizar_feedback_completo.visible)
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=15,
            padding=20
        )
