import flet as ft
from turismo_app.database import db_manager

class GestionInventarioView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")

        # --- Controles para Tipos de Ítem ---
        self.txt_nombre_tipo = ft.TextField(label="Nombre del Tipo de Ítem*")
        self.txt_categoria_tipo = ft.TextField(label="Categoría")
        self.txt_stock_minimo = ft.TextField(label="Stock Mínimo Deseado", keyboard_type=ft.KeyboardType.NUMBER)
        self.btn_guardar_tipo = ft.ElevatedButton("Guardar Tipo", on_click=self._guardar_tipo_handler)
        self.tabla_tipos = ft.DataTable(columns=[ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Categoría")), ft.DataColumn(ft.Text("Stock Mínimo"))])

        # --- Controles para Ítems Individuales ---
        self.dd_tipo_item = ft.Dropdown(label="Tipo de Ítem*")
        self.txt_cantidad_nuevos = ft.TextField(label="Cantidad a Registrar*", value="1", keyboard_type=ft.KeyboardType.NUMBER)
        self.dp_fecha_compra = ft.DatePicker()
        self.btn_fecha_compra = ft.OutlinedButton("Fecha de Compra", on_click=lambda _: self.page.open(self.dp_fecha_compra))
        self.btn_registrar_items = ft.ElevatedButton("Registrar Ítems", on_click=self._registrar_items_handler)
        self.tabla_items = ft.DataTable(columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Tipo")), ft.DataColumn(ft.Text("Estado")), ft.DataColumn(ft.Text("Usos"))])

    def _guardar_tipo_handler(self, e):
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_tipo": self.txt_nombre_tipo.value,
            "categoria": self.txt_categoria_tipo.value,
            "stock_minimo_deseado": int(self.txt_stock_minimo.value),
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_tipo_item(datos)
        self._cargar_tipos_item()

    def _registrar_items_handler(self, e):
        for _ in range(int(self.txt_cantidad_nuevos.value)):
            datos = {
                "id_tipo_item": self.dd_tipo_item.value,
                "estado": "En Almacén",
                "fecha_compra": self.dp_fecha_compra.value.strftime("%Y-%m-%d"),
            }
            db_manager.registrar_item_individual(datos)
        # Lógica para recargar la lista de ítems

    def _cargar_tipos_item(self):
        tipos = db_manager.listar_tipos_item_por_empresa(self.empresa_id)
        self.tabla_tipos.rows.clear()
        self.dd_tipo_item.options.clear()
        for tipo in tipos:
            self.tabla_tipos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(tipo["nombre_tipo"])),
                    ft.DataCell(ft.Text(tipo["categoria"])),
                    ft.DataCell(ft.Text(str(tipo["stock_minimo_deseado"]))),
                ])
            )
            self.dd_tipo_item.options.append(ft.dropdown.Option(tipo["id_tipo_item"], tipo["nombre_tipo"]))
        self.page.update()

    def build(self):
        self._cargar_tipos_item()

        tipos_form = ft.Column([
            self.txt_nombre_tipo,
            self.txt_categoria_tipo,
            self.txt_stock_minimo,
            self.btn_guardar_tipo,
            self.tabla_tipos,
        ])

        items_form = ft.Column([
            self.dd_tipo_item,
            self.txt_cantidad_nuevos,
            self.btn_fecha_compra,
            self.btn_registrar_items,
            self.tabla_items,
        ])

        return ft.Column([
            ft.Text("Gestión de Inventario de Dotación", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Tabs(
                tabs=[
                    ft.Tab(text="Tipos de Ítem", content=tipos_form),
                    ft.Tab(text="Ítems Individuales", content=items_form),
                ]
            )
        ])
