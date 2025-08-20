import flet as ft
import os
import asyncio
from ...ai_agents.corps.formacion_cultura_colonel import get_formacion_cultura_colonel_graph
from ...ai_agents.corps.formacion_deportes_colonel import get_formacion_deportes_colonel_graph

class GestionAgentesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.cultura_colonel = get_formacion_cultura_colonel_graph()
        self.deportes_colonel = get_formacion_deportes_colonel_graph()

        # --- Controles de la UI ---
        self.txt_api_key = ft.TextField(label="OpenAI API Key", password=True, can_reveal_password=True)
        self.dd_corps = ft.Dropdown(
            label="Seleccionar Cuerpo de Ejército",
            options=[
                ft.dropdown.Option("Cultura"),
                ft.dropdown.Option("Deportes"),
            ]
        )
        self.txt_order = ft.TextField(label="Orden para el Coronel", multiline=True, min_lines=3)
        self.btn_send_order = ft.ElevatedButton("Enviar Orden", on_click=self.send_order_handler)
        self.progress_ring = ft.ProgressRing(visible=False)
        self.report_container = ft.Markdown(
            "El informe del coronel aparecerá aquí.",
            selectable=True,
            extension_set="git-hub-flavored",
            code_theme="atom-one-dark"
        )

    async def send_order_handler(self, e):
        api_key = self.txt_api_key.value
        corps = self.dd_corps.value
        order = self.txt_order.value

        if not all([api_key, corps, order]):
            # Mostrar error
            return

        os.environ["OPENAI_API_KEY"] = api_key

        self.progress_ring.visible = True
        self.report_container.value = "Procesando orden..."
        self.page.update()

        selected_agent = None
        if corps == "Cultura":
            selected_agent = self.cultura_colonel
        elif corps == "Deportes":
            selected_agent = self.deportes_colonel

        if selected_agent:
            try:
                # La invocación del agente es asíncrona
                final_state = await selected_agent.ainvoke({"general_order": order})
                self.report_container.value = final_state.get("final_report", "No se generó un informe final.")
            except Exception as ex:
                self.report_container.value = f"Ocurrió un error al ejecutar la orden: {ex}"

        self.progress_ring.visible = False
        self.page.update()


    def build(self):
        return ft.Column(
            controls=[
                ft.Text("Gestión de Agentes de IA", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                self.txt_api_key,
                self.dd_corps,
                self.txt_order,
                self.btn_send_order,
                self.progress_ring,
                ft.Divider(),
                ft.Text("Informe de Misión", style=ft.TextThemeStyle.TITLE_MEDIUM),
                self.report_container,
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=20,
            padding=30,
        )
