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
        self.sw_disponible = ft.Switch(label="Disponible", value=True)

        self.category_dropdowns_container = ft.Column(spacing=10)
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
        self._cargar_productos()
        self._reset_form()

    def _guardar_handler(self, e):
        # Obtener la categoría más específica seleccionada
        selected_category_id = None
        if self.category_dropdowns_container.controls:
            last_dropdown = self.category_dropdowns_container.controls[-1]
            if last_dropdown.value:
                selected_category_id = int(last_dropdown.value)

        datos = {
            "id_empresa": self.empresa_id,
            "nombre_producto": self.txt_nombre.value,
            "descripcion": self.txt_descripcion.value,
            "precio": float(self.txt_precio.value),
            "id_categoria": selected_category_id,
            "disponible": self.sw_disponible.value,
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_producto_menu(datos, self.producto_id_actual)
        self._cargar_productos()
        self._reset_form()
        self.page.update()

    def _cargar_productos(self):
        productos = db_manager.listar_menu_por_empresa(self.empresa_id)
        self.tabla_productos.rows.clear()
        for p in productos:
            self.tabla_productos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p["nombre_producto"])),
                    ft.DataCell(ft.Text(p.get("nombre_categoria", "N/A"))),
                    ft.DataCell(ft.Text(f"{p['precio']:.2f}")),
                    ft.DataCell(ft.Switch(value=bool(p["disponible"]), disabled=True)),
                    ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, data=p, on_click=self._editar_handler)),
                ])
            )

    def _editar_handler(self, e):
        p = e.control.data
        self.producto_id_actual = p["id_producto"]
        self.txt_nombre.value = p["nombre_producto"]
        self.txt_descripcion.value = p["descripcion"]
        self.txt_precio.value = str(p["precio"])
        self.sw_disponible.value = bool(p["disponible"])

        # Cargar jerarquía de categorías
        self.category_dropdowns_container.controls.clear()
        if p.get("id_categoria"):
            path = db_manager.get_category_path(p["id_categoria"])
            parent_id = None
            for category_in_path in path:
                dropdown = self._crear_dropdown_categoria(parent_id, selected_id=str(category_in_path['id_categoria']))
                if dropdown:
                    self.category_dropdowns_container.controls.append(dropdown)
                    parent_id = category_in_path['id_categoria']
        else:
            self._reset_category_dropdowns()

        self.btn_guardar.text = "Actualizar"
        self.page.update()

    def _reset_form(self):
        self.producto_id_actual = None
        self.txt_nombre.value = ""
        self.txt_descripcion.value = ""
        self.txt_precio.value = ""
        self.sw_disponible.value = True
        self.btn_guardar.text = "Guardar"
        self._reset_category_dropdowns()

    def _reset_category_dropdowns(self):
        self.category_dropdowns_container.controls.clear()
        initial_dropdown = self._crear_dropdown_categoria(parent_id=None)
        if initial_dropdown:
            self.category_dropdowns_container.controls.append(initial_dropdown)

    def _crear_dropdown_categoria(self, parent_id, selected_id=None):
        options = [ft.dropdown.Option(str(cat['id_categoria']), cat['nombre_categoria']) for cat in db_manager.get_categorias_by_parent_id(parent_id)]
        if not options: return None
        return ft.Dropdown(label="Categoría", options=options, value=selected_id, on_change=self._on_category_change)

    def _on_category_change(self, e):
        selected_id = int(e.control.value)
        current_index = self.category_dropdowns_container.controls.index(e.control)
        self.category_dropdowns_container.controls = self.category_dropdowns_container.controls[:current_index + 1]
        new_dropdown = self._crear_dropdown_categoria(selected_id)
        if new_dropdown:
            self.category_dropdowns_container.controls.append(new_dropdown)
        self.page.update()

    def build(self):
        formulario = ft.Column([
            self.txt_nombre,
            self.txt_descripcion,
            self.txt_precio,
            ft.Text("Categoría del Producto", weight=ft.FontWeight.BOLD),
            self.category_dropdowns_container,
            self.sw_disponible,
            self.btn_guardar,
            ft.TextButton("Limpiar Formulario", on_click=lambda e: self._reset_form() or self.page.update())
        ])

        return ft.Column([
            ft.Text("Gestión de Menú", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Tabs(tabs=[
                ft.Tab(text="Nuevo/Editar Producto", content=formulario),
                ft.Tab(text="Listado de Productos", content=ft.Column([self.tabla_productos], scroll=ft.ScrollMode.ALWAYS)),
            ])
        ])
