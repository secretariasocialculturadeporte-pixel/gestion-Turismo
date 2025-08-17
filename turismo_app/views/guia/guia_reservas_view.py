import flet as ft
from turismo_app.database import db_manager

class GuiaReservasView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.guia_id = page.session.get("user_id")

        # Tabla de reservas
        self.tabla_reservas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Fecha y Hora")),
                ft.DataColumn(ft.Text("Duración (hrs)")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ]
        )

    def _cargar_reservas(self):
        reservas = db_manager.listar_reservas_tours_por_guia(self.guia_id) # Asume que esta función existe
        self.tabla_reservas.rows.clear()
        for r in reservas:
            self.tabla_reservas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r["nombre_cliente"])),
                        ft.DataCell(ft.Text(r["fecha_hora_inicio"])),
                        ft.DataCell(ft.Text(str(r["duracion_horas"]))),
                        ft.DataCell(ft.Text(r["estado"])),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.CHECK, on_click=self._confirmar_reserva, data=r["id_reserva_tour"]),
                            ft.IconButton(icon=ft.icons.CANCEL, on_click=self._cancelar_reserva, data=r["id_reserva_tour"]),
                        ])),
                    ]
                )
            )
        self.page.update()

    def _confirmar_reserva(self, e):
        # Lógica para confirmar una reserva
        pass

    def _cancelar_reserva(self, e):
        # Lógica para cancelar una reserva
        pass

    def build(self):
        self._cargar_reservas()
        return ft.Column(
            [
                ft.Text("Mis Reservas de Tours", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                self.tabla_reservas,
            ]
        )
