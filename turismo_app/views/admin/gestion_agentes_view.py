import flet as ft
import os
import asyncio
from ...ai_agents.corps.pst_colonel import get_pst_colonel_graph

class GestionAgentesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.pst_colonel = get_pst_colonel_graph()

        # --- Controles de la UI ---
        self.txt_api_key = ft.TextField(label="OpenAI API Key", password=True, can_reveal_password=True)
        self.txt_order = ft.TextField(label="Orden para el Coronel PST", multiline=True, min_lines=3, hint_text="Ej: 'Crear un nuevo torneo de fútbol llamado 'Copa Verano' y abrir inscripciones para 16 equipos.' o 'Añadir un nuevo postre llamado 'Tiramisú' al menú del restaurante.'")
        self.btn_send_order = ft.ElevatedButton("Enviar Orden al Coronel PST", on_click=self.send_order_handler)
        self.progress_ring = ft.ProgressRing(visible=False)
        self.report_container = ft.Markdown(
            "El informe del Coronel PST aparecerá aquí.",
            selectable=True,
            extension_set="git-hub-flavored",
            code_theme="atom-one-dark"
        )

    async def send_order_handler(self, e):
        api_key = self.txt_api_key.value
        order = self.txt_order.value

        if not all([api_key, order]):
            self.report_container.value = "Error: Por favor, introduce tu API Key de OpenAI y una orden."
            self.page.update()
            return

        os.environ["OPENAI_API_KEY"] = api_key

        self.progress_ring.visible = True
        self.report_container.value = "Procesando orden... El Coronel está planificando..."
        self.page.update()

        try:
            # La invocación del agente es asíncrona
            final_state = await self.pst_colonel.ainvoke({"general_order": order})
            self.report_container.value = final_state.get("final_report", "No se generó un informe final.")
        except Exception as ex:
            self.report_container.value = f"Ocurrió un error al ejecutar la orden: {ex}"

        self.progress_ring.visible = False
        self.page.update()

    def build(self):
        return ft.Column(
            controls=[
                ft.Text("Puesto de Mando: Coronel PST", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("Desde aquí puedes dar órdenes de alto nivel al Coronel que comanda a todos los Prestadores de Servicios Turísticos (PST)."),
                self.txt_api_key,
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
