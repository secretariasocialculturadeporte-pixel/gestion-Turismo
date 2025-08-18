import flet as ft
from turismo_app.agents import turismo_agent

class ChatMessage(ft.Row):
    """Un control para mostrar un único mensaje en el chat."""
    def __init__(self, content: ft.Control | list[ft.Control], is_user: bool):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START

        message_content = content if isinstance(content, list) else [content]

        self.controls = [
            ft.CircleAvatar(
                content=ft.Icon(ft.icons.PERSON if is_user else ft.icons.ASSISTANT),
                bgcolor=ft.colors.BLUE_GREY_200 if is_user else ft.colors.TEAL_200,
            ),
            ft.Column(
                [
                    ft.Text("Tú" if is_user else "Asistente", weight=ft.FontWeight.BOLD),
                    *message_content,
                ],
                tight=True,
                spacing=5,
            ),
        ]

class ChatbotView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.agent = turismo_agent.app # El grafo compilado de LangGraph

        self.expand = True
        self.spacing = 10
        self.padding = 15

        # Controles de la UI
        self.chat_history = ft.ListView(expand=True, spacing=10, auto_scroll=True)
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

        self._add_message(ft.Text("¡Hola! Soy tu Asistente de Viajes. ¿Qué plan tienes en mente?"), is_user=False)

        self.controls = [
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
        ]

    def _add_message(self, content: ft.Control | list[ft.Control], is_user: bool):
        self.chat_history.controls.append(ChatMessage(content, is_user))
        self.update()

    def send_message_click(self, e):
        user_message = self.new_message.value
        if not user_message:
            return

        self._add_message(ft.Text(user_message), is_user=True)

        self.new_message.value = ""
        self.progress_ring.visible = True
        self.send_button.disabled = True
        self.update()

        agent_response = turismo_agent.invoke_agent(user_message)

        # Aquí se manejaría una respuesta estructurada del agente
        # Por ahora, solo mostramos el texto
        self.progress_ring.visible = False
        self.send_button.disabled = False
        self._add_message(ft.Text(agent_response), is_user=False)
        self.new_message.focus()
        self.update()
