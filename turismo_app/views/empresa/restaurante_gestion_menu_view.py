import flet as ft
from turismo_app.database import db_manager

class RestauranteGestionMenuView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.producto_id_actual = None

        # Controles del formulario
        self.txt_nombre = ft.TextField(label="Nombre del Producto*")
        self.txt_descripcion = ft.TextField(label="Descripción", multiline=True)
        self.txt_precio = ft.TextField(label="Precio (COP)*", keyboard_type=ft.KeyboardType.NUMBER)
        self.dd_categoria = ft.Dropdown(
            label="Categoría*",
            options=[
                ft.dropdown.Option("Entradas"),
                ft.dropdown.Option("Platos Fuertes"),
                ft.dropdown.Option("Bebidas"),
                ft.dropdown.Option("Postres"),
            ]
        )
        self.sw_disponible = ft.Switch(label="Disponible", value=True)
        self.btn_guardar = ft.ElevatedButton("Guardar", on_click=self._guardar_handler)

        # Tabla de productos
        self.tabla_productos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Disponible")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_handler(self, e):
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_producto": self.txt_nombre.value,
            "descripcion": self.txt_descripcion.value,
            "precio": float(self.txt_precio.value),
            "categoria": self.dd_categoria.value,
            "disponible": self.sw_disponible.value,
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_producto_menu(datos, self.producto_id_actual)
        self._cargar_productos()

    def _cargar_productos(self):
        productos = db_manager.listar_menu_por_empresa(self.empresa_id)
        self.tabla_productos.rows.clear()
        for p in productos:
            self.tabla_productos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p["nombre_producto"])),
                        ft.DataCell(ft.Text(p["categoria"])),
                        ft.DataCell(ft.Text(f"{p['precio']:.2f}")),
                        ft.DataCell(ft.Switch(value=bool(p["disponible"]), disabled=True)),
                        ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, data=p, on_click=self._editar_handler)),
                    ]
                )
            )
        self.page.update()

    def _editar_handler(self, e):
        p = e.control.data
        self.producto_id_actual = p["id_producto"]
        self.txt_nombre.value = p["nombre_producto"]
        self.txt_descripcion.value = p["descripcion"]
        self.txt_precio.value = str(p["precio"])
        self.dd_categoria.value = p["categoria"]
        self.sw_disponible.value = bool(p["disponible"])
        self.btn_guardar.text = "Actualizar"
        self.page.update()

    def build(self):
        self._cargar_productos()
        formulario = ft.Column([
            self.txt_nombre,
            self.txt_descripcion,
            self.txt_precio,
            self.dd_categoria,
            self.sw_disponible,
            self.btn_guardar,
        ])

        return ft.Column(
            [
                ft.Text("Gestión de Menú", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nuevo/Editar Producto", content=formulario),
                        ft.Tab(text="Listado de Productos", content=ft.Column([self.tabla_productos])),
                    ]
                )
            ]
        )
