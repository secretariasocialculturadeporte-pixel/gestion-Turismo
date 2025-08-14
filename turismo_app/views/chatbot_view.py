import flet as ft
from turismo_app.agents import turismo_agent

class ChatMessage(ft.Row):
    """Un control para mostrar un único mensaje en el chat."""
    def __init__(self, message: str, is_user: bool):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Icon(ft.icons.PERSON if is_user else ft.icons.ASSISTANT),
                bgcolor=ft.colors.BLUE_GREY_200 if is_user else ft.colors.TEAL_200,
            ),
            ft.Column(
                [
                    ft.Text(
                        "Tú" if is_user else "Asistente",
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(message, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

class ChatbotView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.agent = None # Se inicializará en did_mount

        # Controles de la UI
        self.chat_history = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )
        self.new_message = ft.TextField(
            hint_text="Escribe tu pregunta aquí...",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=self.send_message_click,
        )
        self.send_button = ft.IconButton(
            icon=ft.icons.SEND_ROUNDED,
            tooltip="Enviar Mensaje",
            on_click=self.send_message_click,
        )
        self.progress_ring = ft.ProgressRing(visible=False)

    def did_mount(self):
        # Crear el agente cuando la vista se monte
        self.agent = turismo_agent.create_turismo_agent()
        # Enviar un mensaje de bienvenida inicial
        self._add_message("¡Hola! Soy el Asistente de Turismo. Pregúntame sobre empresas o atractivos.", is_user=False)
        self.update()

    def _add_message(self, message: str, is_user: bool):
        self.chat_history.controls.append(ChatMessage(message, is_user))
        self.update()

    def send_message_click(self, e):
        user_message = self.new_message.value
        if not user_message:
            return

        self._add_message(user_message, is_user=True)

        # Limpiar el campo de texto y mostrar el indicador de progreso
        self.new_message.value = ""
        self.progress_ring.visible = True
        self.send_button.disabled = True
        self.update()

        # Invocar al agente y obtener la respuesta
        agent_response = turismo_agent.invoke_agent(self.agent, user_message)

        # Ocultar el indicador de progreso y mostrar la respuesta
        self.progress_ring.visible = False
        self.send_button.disabled = False
        self._add_message(agent_response, is_user=False)
        self.new_message.focus()
        self.update()

    def build(self):
        return ft.Column(
            [
                ft.Text("Asistente Virtual de Turismo", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Divider(),
                self.chat_history,
                ft.Row(
                    [
                        self.progress_ring,
                        self.new_message,
                        self.send_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            expand=True,
            spacing=10,
            padding=15
        )
