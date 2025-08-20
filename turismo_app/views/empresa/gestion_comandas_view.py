import flet as ft
from turismo_app.database import db_manager

class GestionComandasView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.pedido_actual = {} # {producto_id: {"cantidad": N, "nombre": "...", "precio": X}}

        # --- Controles Principales ---
        self.dd_tipo_orden = ft.Dropdown(
            label="Tipo de Orden",
            options=[
                ft.dropdown.Option("Mesa"),
                ft.dropdown.Option("Delivery"),
                ft.dropdown.Option("Barra"),
                ft.dropdown.Option("Para llevar"),
            ],
            on_change=self._on_tipo_orden_change,
        )

        # --- Contenedor para detalles de la orden ---
        self.detalles_orden_container = ft.Column()

        # --- Controles para detalles de Mesa ---
        self.dd_mesas = ft.Dropdown(label="Seleccionar Mesa")

        # --- Controles para detalles de Delivery ---
        self.txt_cliente_nombre = ft.TextField(label="Nombre del Cliente")
        self.txt_cliente_direccion = ft.TextField(label="Dirección de Entrega")
        self.txt_cliente_telefono = ft.TextField(label="Teléfono de Contacto")

        # --- Contenedor para el menú y el pedido ---
        self.menu_list_view = ft.ListView(expand=True, spacing=10)
        self.pedido_list_view = ft.ListView(expand=True, spacing=10)
        self.txt_total_pedido = ft.Text("Total: $0.00", size=20, weight=ft.FontWeight.BOLD)

        self.btn_guardar_pedido = ft.ElevatedButton("Guardar Pedido", on_click=self._guardar_pedido_handler)

    def _on_tipo_orden_change(self, e):
        tipo = e.control.value
        self.detalles_orden_container.controls.clear()
        if tipo == "Mesa":
            # Cargar mesas y añadirlas al dropdown
            mesas = db_manager.listar_mesas_por_empresa(self.empresa_id)
            self.dd_mesas.options = [ft.dropdown.Option(str(m['id_mesa']), m['nombre_mesa']) for m in mesas]
            self.detalles_orden_container.controls.append(self.dd_mesas)
        elif tipo == "Delivery":
            self.detalles_orden_container.controls.extend([
                self.txt_cliente_nombre,
                self.txt_cliente_direccion,
                self.txt_cliente_telefono,
            ])
        self.page.update()

    def _guardar_pedido_handler(self, e):
        # --- Validación ---
        if not self.dd_tipo_orden.value:
            # Implementar feedback al usuario
            print("Error: Debe seleccionar un tipo de orden.")
            return
        if not self.pedido_actual:
            print("Error: No hay productos en el pedido.")
            return

        # --- Preparar datos ---
        total = sum(item['cantidad'] * item['precio'] for item in self.pedido_actual.values())

        datos_pedido = {
            "id_empresa": self.empresa_id,
            "id_mesero": self.page.session.get("user_id"),
            "tipo_orden": self.dd_tipo_orden.value,
            "id_mesa": int(self.dd_mesas.value) if self.dd_tipo_orden.value == "Mesa" else None,
            "cliente_nombre": self.txt_cliente_nombre.value if self.dd_tipo_orden.value == "Delivery" else None,
            "cliente_direccion": self.txt_cliente_direccion.value if self.dd_tipo_orden.value == "Delivery" else None,
            "cliente_telefono": self.txt_cliente_telefono.value if self.dd_tipo_orden.value == "Delivery" else None,
            "total": total,
        }

        items_pedido = [{
            "id_producto": prod_id,
            "cantidad": details["cantidad"],
            "precio": details["precio"]
        } for prod_id, details in self.pedido_actual.items()]

        # --- Llamar al DB Manager ---
        pedido_id = db_manager.crear_pedido_completo(
            datos_pedido,
            items_pedido,
            self.page.session.get("user_id")
        )

        if pedido_id:
            print(f"Pedido {pedido_id} guardado exitosamente.")
            # Resetear la vista
            self.pedido_actual.clear()
            self._actualizar_vista_pedido()
            self.dd_tipo_orden.value = None
            self.detalles_orden_container.controls.clear()
            self.page.update()
        else:
            print("Error al guardar el pedido.")

    def _cargar_menu(self):
        menu_items = db_manager.listar_menu_por_empresa(self.empresa_id)
        self.menu_list_view.controls.clear()
        for item in menu_items:
            self.menu_list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(item["nombre_producto"]),
                    subtitle=ft.Text(f"${item['precio']:.2f}"),
                    trailing=ft.IconButton(ft.icons.ADD, on_click=self._agregar_al_pedido, data=item),
                )
            )

    def _agregar_al_pedido(self, e):
        producto = e.control.data
        prod_id = producto['id_producto']

        if prod_id in self.pedido_actual:
            self.pedido_actual[prod_id]['cantidad'] += 1
        else:
            self.pedido_actual[prod_id] = {
                "cantidad": 1,
                "nombre": producto['nombre_producto'],
                "precio": producto['precio']
            }
        self._actualizar_vista_pedido()

    def _actualizar_vista_pedido(self):
        self.pedido_list_view.controls.clear()
        total = 0
        for prod_id, details in self.pedido_actual.items():
            total += details['cantidad'] * details['precio']
            self.pedido_list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{details['cantidad']}x {details['nombre']}"),
                    subtitle=ft.Text(f"${details['precio']:.2f} c/u"),
                )
            )
        self.txt_total_pedido.value = f"Total: ${total:,.2f}"
        self.page.update()

    def build(self):
        self._cargar_menu()

        columna_izquierda = ft.Column([
            ft.Text("Nuevo Pedido", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            self.dd_tipo_orden,
            self.detalles_orden_container,
            ft.Divider(),
            ft.Text("Menú", style=ft.TextThemeStyle.TITLE_MEDIUM),
            self.menu_list_view,
        ], expand=4) # 40% del espacio

        columna_derecha = ft.Column([
            ft.Text("Comanda Actual", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            self.pedido_list_view,
            ft.Divider(),
            self.txt_total_pedido,
            self.btn_guardar_pedido
        ], expand=6) # 60% del espacio

        return ft.Row(
            controls=[
                columna_izquierda,
                ft.VerticalDivider(),
                columna_derecha
            ],
            expand=True
        )
