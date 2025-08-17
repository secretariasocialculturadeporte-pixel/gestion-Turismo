import flet as ft
from turismo_app.database import db_manager

class RestauranteKDSView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")

        # Controles
        self.pedidos_container = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            controls=[] # Aquí se cargarán las tarjetas de pedidos
        )

    def _cargar_pedidos(self):
        # Lógica para obtener los pedidos abiertos y sus items
        # Esta es una simplificación. En una app real, esto sería más complejo
        # y probablemente usaría WebSockets para actualizaciones en tiempo real.
        pedidos = db_manager.listar_pedidos_abiertos_por_empresa(self.empresa_id) # Asume que esta función existe

        self.pedidos_container.controls.clear()
        for pedido in pedidos:
            items_pedido = db_manager.listar_items_por_pedido(pedido["id_pedido"]) # Asume que esta función existe

            items_controls = [
                ft.Text(f"{item['cantidad']}x {item['nombre_producto']}") for item in items_pedido
            ]

            self.pedidos_container.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"Mesa: {pedido['nombre_mesa']}", weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            *items_controls,
                            ft.ElevatedButton("Marcar como Listo", on_click=self._marcar_listo_handler, data=pedido["id_pedido"])
                        ]),
                        padding=10,
                        width=250
                    )
                )
            )
        self.page.update()

    def _marcar_listo_handler(self, e):
        # Lógica para actualizar el estado del pedido
        pass

    def build(self):
        self._cargar_pedidos()
        return ft.Column(
            [
                ft.Text("Pedidos en Cocina (KDS)", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Divider(),
                self.pedidos_container,
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )
