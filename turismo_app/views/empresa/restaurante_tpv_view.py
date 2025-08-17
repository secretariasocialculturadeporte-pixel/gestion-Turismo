import flet as ft
from turismo_app.database import db_manager

class RestauranteTPVView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")

        # Controles
        self.plano_mesas = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=150,
            child_aspect_ratio=1.0,
        )

        self.dialogo_pedido = ft.AlertDialog(
            modal=True,
            title=ft.Text("Tomar Pedido"),
            content=ft.Text("Aquí irá el formulario para añadir productos al pedido."),
        )

    def _abrir_pedido(self, e):
        mesa = e.control.data
        self.dialogo_pedido.title = ft.Text(f"Pedido para: {mesa['nombre_mesa']}")

        # Lógica para cargar el menú y mostrarlo en el diálogo
        menu_items = db_manager.listar_menu_por_empresa(self.empresa_id)

        def agregar_al_pedido(e):
            producto = e.control.data
            # Lógica para agregar el producto al pedido actual
            print(f"Agregando {producto['nombre_producto']} al pedido.")

        menu_controls = [
            ft.ListTile(
                title=ft.Text(item["nombre_producto"]),
                subtitle=ft.Text(f"${item['precio']:.2f}"),
                on_click=agregar_al_pedido,
                data=item
            ) for item in menu_items
        ]

        self.dialogo_pedido.content = ft.Column(menu_controls, scroll=ft.ScrollMode.ADAPTIVE)
        self.dialogo_pedido.open = True
        self.page.update()

    def build(self):
        self.page.dialog = self.dialogo_pedido

        mesas = db_manager.listar_mesas_por_empresa(self.empresa_id)
        self.plano_mesas.controls.clear()
        for mesa in mesas:
            self.plano_mesas.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Text(mesa["nombre_mesa"]),
                        alignment=ft.alignment.center,
                        bgcolor=ft.colors.GREEN_200 if mesa["estado"] == "Libre" else ft.colors.RED_200,
                        on_click=self._abrir_pedido,
                        data=mesa,
                    )
                )
            )

        return ft.Column(
            [
                ft.Text("Plano de Mesas (TPV)", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                self.plano_mesas,
            ]
        )
