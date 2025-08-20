import flet as ft
from turismo_app.database import db_manager

class GestionDashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.estados_posibles = ["Recibido", "En Preparación", "Listo para Entregar", "Cerrado"]

        # Crear columnas para cada estado
        self.columnas_estado = {
            estado: ft.Column(
                controls=[ft.Text(estado, style=ft.TextThemeStyle.HEADLINE_SMALL)],
                scroll=ft.ScrollMode.ADAPTIVE,
                expand=True
            ) for estado in self.estados_posibles
        }

    def _mover_pedido(self, e):
        pedido_id = e.control.data['id_pedido']
        estado_actual = e.control.data['estado_actual']

        # Encontrar el próximo estado
        try:
            indice_actual = self.estados_posibles.index(estado_actual)
            nuevo_estado = self.estados_posibles[indice_actual + 1]
        except (ValueError, IndexError):
            nuevo_estado = "Cerrado"

        # Actualizar en la base de datos
        db_manager.actualizar_estado_pedido(pedido_id, nuevo_estado, self.page.session.get("user_id"))

        # Recargar la vista
        self._cargar_pedidos()
        self.page.update()

    def _crear_card_pedido(self, pedido):
        items = db_manager.get_items_por_pedido(pedido['id_pedido'])
        items_controls = [ft.Text(f"- {item['cantidad']}x {item['nombre_producto']}") for item in items]

        # Determinar el título del pedido
        if pedido['tipo_orden'] == 'Mesa':
            titulo = f"Mesa: {pedido.get('nombre_mesa', 'N/A')}"
        elif pedido['tipo_orden'] == 'Delivery':
            titulo = f"Delivery: {pedido.get('cliente_nombre', 'N/A')}"
        else:
            titulo = f"Pedido #{pedido['id_pedido']}"

        return ft.Card(
            elevation=4,
            content=ft.Container(
                padding=10,
                content=ft.Column([
                    ft.Text(titulo, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Tipo: {pedido['tipo_orden']}"),
                    ft.Divider(),
                    *items_controls,
                    ft.Divider(),
                    ft.ElevatedButton(
                        text="Siguiente Estado",
                        on_click=self._mover_pedido,
                        data={'id_pedido': pedido['id_pedido'], 'estado_actual': pedido['estado']}
                    )
                ])
            )
        )

    def _cargar_pedidos(self):
        # Limpiar todas las columnas
        for columna in self.columnas_estado.values():
            # No borrar el título
            columna.controls = [columna.controls[0]]

        pedidos = db_manager.get_pedidos_abiertos_por_empresa(self.empresa_id)
        for pedido in pedidos:
            estado = pedido['estado']
            if estado in self.columnas_estado:
                card = self._crear_card_pedido(pedido)
                self.columnas_estado[estado].controls.append(card)

    def build(self):
        self._cargar_pedidos()

        return ft.Column([
            ft.Text("Dashboard de Comandas en Tiempo Real", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Row(
                controls=list(self.columnas_estado.values()),
                expand=True,
            )
        ])
