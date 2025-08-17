import flet as ft
from turismo_app.database import db_manager

class AgenciaGestionPaquetesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")
        self.paquete_id_actual = None

        # Controles del formulario
        self.txt_nombre_paquete = ft.TextField(label="Nombre del Paquete*")
        self.txt_descripcion = ft.TextField(label="Descripción", multiline=True)
        self.txt_precio = ft.TextField(label="Precio Total (COP)*", keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_duracion = ft.TextField(label="Duración (días)*", keyboard_type=ft.KeyboardType.NUMBER)
        self.sw_activo = ft.Switch(label="Activo", value=True)
        self.btn_guardar = ft.ElevatedButton("Guardar Paquete", on_click=self._guardar_handler)

        # Tabla de paquetes
        self.tabla_paquetes = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Duración")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _guardar_handler(self, e):
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_paquete": self.txt_nombre_paquete.value,
            "descripcion": self.txt_descripcion.value,
            "precio_total": float(self.txt_precio.value),
            "duracion_dias": int(self.txt_duracion.value),
            "activo": self.sw_activo.value,
            "audit_user_id": self.page.session.get("user_id")
        }
        db_manager.crear_o_actualizar_paquete(datos, self.paquete_id_actual)
        self._cargar_paquetes()

    def _cargar_paquetes(self):
        paquetes = db_manager.listar_paquetes_por_agencia(self.empresa_id)
        self.tabla_paquetes.rows.clear()
        for p in paquetes:
            self.tabla_paquetes.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p["nombre_paquete"])),
                        ft.DataCell(ft.Text(f"{p['precio_total']:.2f}")),
                        ft.DataCell(ft.Text(str(p["duracion_dias"]))),
                        ft.DataCell(ft.Switch(value=bool(p["activo"]), disabled=True)),
                        ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, data=p, on_click=self._editar_handler)),
                    ]
                )
            )
        self.page.update()

    def _editar_handler(self, e):
        p = e.control.data
        self.paquete_id_actual = p["id_paquete"]
        self.txt_nombre_paquete.value = p["nombre_paquete"]
        self.txt_descripcion.value = p["descripcion"]
        self.txt_precio.value = str(p["precio_total"])
        self.txt_duracion.value = str(p["duracion_dias"])
        self.sw_activo.value = bool(p["activo"])
        self.btn_guardar.text = "Actualizar Paquete"
        self.page.update()

    def build(self):
        self._cargar_paquetes()
        formulario = ft.Column([
            self.txt_nombre_paquete,
            self.txt_descripcion,
            self.txt_precio,
            self.txt_duracion,
            self.sw_activo,
            self.btn_guardar,
        ])

        return ft.Column(
            [
                ft.Text("Gestión de Paquetes Turísticos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Tabs(
                    tabs=[
                        ft.Tab(text="Nuevo/Editar Paquete", content=formulario),
                        ft.Tab(text="Listado de Paquetes", content=ft.Column([self.tabla_paquetes])),
                    ]
                )
            ]
        )
