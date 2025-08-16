import flet as ft
from turismo_app.database import db_manager
import logging

logger = logging.getLogger(__name__)

class LoginView(ft.Column):
    def __init__(self, page: ft.Page, on_login_success: callable):
        super().__init__()
        self.page = page
        self.on_login_success_callback = on_login_success

        self.horizontal_alignment = "center"
        self.spacing = 15

        # --- Controles ---
        self.usuario = ft.TextField(label="Usuario", autofocus=True, width=300)
        self.clave = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
        self.boton_login = ft.ElevatedButton(
            "Ingresar",
            on_click=self.iniciar_sesion,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=20)
        )

        # --- Contenedor Principal ---
        login_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Iniciar Sesión", size=22, weight="bold"),
                    self.usuario,
                    self.clave,
                    self.boton_login
                ],
                horizontal_alignment="center",
                spacing=15
            ),
            width=400,
            padding=30,
            border_radius=15,
            bgcolor=ft.colors.SURFACE_VARIANT,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=2, color=ft.colors.BLACK12)
        )

        self.controls = [login_card]

    def iniciar_sesion(self, e):
        username = self.usuario.value
        password = self.clave.value

        if not username or not password:
            self.page.snack_bar = ft.SnackBar(ft.Text("❌ Por favor, ingrese usuario y contraseña"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        user_data_db = db_manager.obtener_usuario_por_nombre(username)

        if user_data_db and db_manager.verify_password(password, user_data_db.get('password_hash')):
            if user_data_db.get('activo'):
                self.page.snack_bar = ft.SnackBar(ft.Text("✅ Bienvenido al sistema"))
                self.page.snack_bar.open = True
                self.on_login_success_callback(user_data_db)
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("❌ Cuenta de usuario desactivada."))
                self.page.snack_bar.open = True
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("❌ Usuario o contraseña incorrectos"))
            self.page.snack_bar.open = True

        self.page.update()
