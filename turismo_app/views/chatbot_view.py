import flet as ft
import os
import asyncio
from turismo_app.database import db_manager
from turismo_app.ai_agents.corps.pst_colonel import get_pst_colonel_graph

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
                    ft.Text("Tú" if is_user else "Asistente PST", weight=ft.FontWeight.BOLD),
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
        self.agent = get_pst_colonel_graph()

        self.expand = True
        self.spacing = 10
        self.padding = 15

        # Controles de la UI
        self.chat_history = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.new_message = ft.TextField(
            hint_text="Da una orden al Asistente de Turismo...",
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

        self._add_message(ft.Text("¡Hola! Soy el Asistente de Turismo PST. ¿Qué necesitas?"), is_user=False)

        self.controls = [
            ft.Text("Asistente Virtual de Turismo (PST)", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
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

    async def send_message_click(self, e):
        user_message = self.new_message.value
        if not user_message:
            return

        self._add_message(ft.Text(user_message), is_user=True)

        self.new_message.value = ""
        self.progress_ring.visible = True
        self.send_button.disabled = True
        self.update()

        # Obtener la API Key y configurar el entorno
        api_key = db_manager.obtener_configuracion('OPENAI_API_KEY')
        if not api_key:
            self._add_message(ft.Text("Error: La API Key de OpenAI no está configurada por un administrador."), is_user=False)
            self.progress_ring.visible = False
            self.send_button.disabled = False
            self.update()
            return

        os.environ["OPENAI_API_KEY"] = api_key

        agent_response = "Error desconocido."
        try:
            # Invocar al Coronel PST
            final_state = await self.agent.ainvoke({"general_order": user_message})
            agent_response = final_state.get("final_report", "La misión concluyó sin un informe final.")
        except Exception as ex:
            agent_response = f"Ocurrió un error al procesar tu solicitud: {ex}"

        self.progress_ring.visible = False
        self.send_button.disabled = False
        self._add_message(ft.Markdown(agent_response, selectable=True, extension_set="git-hub-flavored", code_theme="atom-one-dark"), is_user=False)
        self.new_message.focus()
        self.update()
