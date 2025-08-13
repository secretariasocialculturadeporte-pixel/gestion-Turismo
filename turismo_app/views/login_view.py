import flet as ft
from turismo_app.database import db_manager
import logging

logger = logging.getLogger(__name__)

class LoginView(ft.Control):
    def __init__(self, page: ft.Page, on_login_success: callable, on_navigate_to_register: callable = None):
        """
        Vista de Inicio de Sesión

        Args:
            page: La instancia de la página Flet.
            on_login_success: Callback a llamar cuando el login es exitoso. Debe aceptar un diccionario con los datos del usuario.
            on_navigate_to_register: Callback opcional para navegar a una vista de registro.
        """
        super().__init__()
        self.page = page
        self.on_login_success_callback = on_login_success
        self.on_navigate_to_register_callback = on_navigate_to_register

        # --- Controles del formulario de inicio de sesión ---
        self.username_field = ft.TextField(
            label="Nombre de usuario o Email",
            hint_text="Ingrese su identificador de acceso",
            autofocus=True,
            prefix_icon=ft.icons.PERSON_OUTLINE_ROUNDED,
            border_radius=8,
            dense=True,
            text_size=14,
            on_submit=self._handle_login_attempt  # Permite iniciar sesión con Enter
        )
        self.password_field = ft.TextField(
            label="Contraseña",
            hint_text="Ingrese su contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK_OUTLINE_ROUNDED,
            border_radius=8,
            dense=True,
            text_size=14,
            on_submit=self._handle_login_attempt  # Permite iniciar sesión con Enter
        )
        self.error_message_text = ft.Text(
            value="",
            color=ft.colors.ERROR,
            visible=False,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER
        )
        self.login_button = ft.ElevatedButton(
            text="Ingresar al Sistema",
            icon=ft.icons.LOGIN_ROUNDED,
            on_click=self._handle_login_attempt,
            width=280,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                # bgcolor={ft.MaterialState.HOVERED: ft.colors.GREEN_ACCENT_700}, # Ejemplo de estilo
            )
        )
        self.loading_indicator_login = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2.5)

        # (Opcional) Enlace a registro de ciudadano
        registro_link_controls = []
        if self.on_navigate_to_register_callback:
            registro_link_controls.append(ft.Container(height=10))
            registro_link_controls.append(
                ft.TextButton(
                    content=ft.Row(
                        [ft.Text("¿Nuevo ciudadano? "), ft.Text("Regístrese aquí", weight=ft.FontWeight.BOLD)],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    on_click=lambda _: self.on_navigate_to_register_callback("/ciudadano/registro"), # Asume una ruta de registro
                    width=280
                )
            )

        # --- Diseño principal de la vista de inicio de sesión ---
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        # ft.Image(src="/icons/logo_app_login.png", width=100, height=100, fit=ft.ImageFit.CONTAIN), # Ajusta la ruta de tu logotipo
                        ft.Text("Bienvenido", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text("Sistema Integrado de Gestión Turística Territorial", size=16, color=ft.colors.OUTLINE, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=25),
                        self.username_field,
                        self.password_field,
                        ft.Container(height=5),
                        self.error_message_text,
                        ft.Container(height=15),
                        ft.Row(
                            [self.login_button, self.loading_indicator_login],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        *registro_link_controls,  # Desempaquetar si hay un enlace de registro
                        ft.Container(height=20),
                        ft.TextButton(
                            "¿Olvidó su contraseña?",
                            on_click=self._handle_forgot_password,  # Implementar esta lógica después
                            width=280,
                            style=ft.ButtonStyle(color=ft.colors.PRIMARY)
                        )
                    ],
                    width=400, # Ancho del formulario
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    spacing=12
                ),
                width=450, # Ancho del contenedor de la tarjeta
                padding=ft.padding.symmetric(horizontal=30, vertical=40),
                border_radius=12,
                bgcolor=ft.colors.SURFACE_VARIANT, # Un fondo adecuado para la tarjeta
                # ink=True, # Efecto de clic
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.colors.with_opacity(0.15, ft.colors.BLACK))
            )
        ]
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.expand = True # Para que el contenedor principal ocupe el espacio de la vista

    def _show_error_message(self, message: str):
        self.error_message_text.value = message
        self.error_message_text.visible = True
        self.update()

    def _clear_error_message(self):
        self.error_message_text.visible = False
        self.update()

    def _set_loading_state(self, is_loading: bool):
        self.login_button.disabled = is_loading
        self.loading_indicator_login.visible = is_loading
        self.username_field.disabled = is_loading
        self.password_field.disabled = is_loading
        self.update()

    def _handle_login_attempt(self, e):
        self._clear_error_message()
        username = self.username_field.value.strip()
        password = self.password_field.value

        if not username or not password:
            self._show_error_message("Por favor, ingrese su usuario y contraseña.")
            return

        self._set_loading_state(True)
        try:
            # Intenta obtener por nombre de usuario o correo electrónico
            user_data_db = db_manager.obtener_usuario_por_nombre(username)

            if not user_data_db and "@" in username:
                # Si no lo encontré por nombre de usuario y es un correo electrónico
                # Aquí podrías tener una función db_manager.obtener_usuario_por_email(username)
                # logger.info(f"Intento de inicio de sesión con correo electrónico: {username}, buscando por correo electrónico si función existe.")
                # user_data_db = db_manager.obtener_usuario_por_email(username) # Requeriría esta función
                pass # Por ahora, solo por nombre de usuario

            if user_data_db:
                if user_data_db['activo'] == 0:
                    self._show_error_message("Su cuenta de usuario ha sido desactivada. Contacte al administrador.")
                    logger.warning(f"Intento de login fallido (cuenta desactivada): {username}")
                elif db_manager.verify_password(password, user_data_db['password_hash']):
                    logger.info(f"Login exitoso para usuario: {username}. Datos de usuario: {dict(user_data_db)}")
                    self.on_login_success_callback(dict(user_data_db)) # Enviar dict
                else:
                    self._show_error_message("Nombre de usuario o contraseña incorrectos.")
                    logger.warning(f"Intento de inicio de sesión fallido (contraseña incorrecta): {username}")
            else:
                self._show_error_message("Nombre de usuario o contraseña incorrectos.")
                logger.warning(f"Intento de inicio de sesión fallido (usuario no encontrado): {username}")

        except Exception as ex:
            logger.error(f"Error inesperado durante el intento de inicio de sesión para '{username}': {ex}", exc_info=True)
            self._show_error_message("Ocurrió un error inesperado. Por favor, intente más tarde.")
        finally:
            self._set_loading_state(False)
            self.username_field.focus() # Devolver foco al campo usuario

    def _handle_forgot_password(self, e):
        # Esta es una funcionalidad más avanzada que requiere envío de correos electrónicos.
        # Por ahora, podemos mostrar un mensaje informativo.
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Recuperar Contraseña"),
            content=ft.Text("Si olvidó su contraseña, por favor contacte al administrador del sistema para solicitar un reseteo."),
            actions=[ft.TextButton("Entendido", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

# Si necesitas que este archivo se pueda ejecutar independientemente para pruebas de UI (muy básico)
if __name__ == '__main__':
    def _mock_login_success(user_data):
        print("Login Exitoso (Mock):", user_data.get("nombre_usuario"))
        # En una aplicación real, page.go("/") o page.go("/dashboard")

    def _mock_navigate_register(route):
        print(f"Navegar a registro (Mock): {route}")

    def main_test(page: ft.Page):
        page.title = "Prueba Login View"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        login_control = LoginView(page, on_login_success=_mock_login_success, on_navigate_to_register=_mock_navigate_register)
        page.add(login_control)

    ft.app(target=main_test)
