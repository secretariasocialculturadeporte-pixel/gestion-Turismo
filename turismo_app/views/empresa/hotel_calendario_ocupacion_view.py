import flet as ft
from turismo_app.database import db_manager
import datetime

class HotelCalendarioOcupacionView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.empresa_id = page.session.get("user_id_empresa_asociada")

        # Controles
        self.calendario_grid = ft.GridView(
            expand=True,
            runs_count=5, # Muestra 5 días a la vez, por ejemplo
            max_extent=150,
            child_aspect_ratio=1.0,
        )

    def build(self):
        habitaciones = db_manager.listar_habitaciones_por_empresa(self.empresa_id)

        dias_a_mostrar = 30
        hoy = datetime.date.today()

        header_row = ft.Row([ft.Container(ft.Text("Habitación"), width=150, alignment=ft.alignment.center)])
        for i in range(dias_a_mostrar):
            fecha = hoy + datetime.timedelta(days=i)
            header_row.controls.append(
                ft.Container(
                    content=ft.Text(f"{fecha.strftime('%d/%m')}", text_align=ft.TextAlign.CENTER),
                    width=60,
                    alignment=ft.alignment.center
                )
            )

        cuerpo_calendario = ft.Column()
        for hab in habitaciones:
            reservas = db_manager.listar_reservas_por_habitacion(hab["id_habitacion"])
            row = ft.Row([ft.Container(ft.Text(hab["nombre_habitacion"]), width=150)])
            for i in range(dias_a_mostrar):
                fecha = hoy + datetime.timedelta(days=i)
                ocupado = any(
                    res["fecha_inicio"] <= fecha.isoformat() <= res["fecha_fin"]
                    for res in reservas
                )
                row.controls.append(
                    ft.Container(
                        width=60,
                        height=40,
                        bgcolor=ft.colors.RED_200 if ocupado else ft.colors.GREEN_200,
                        border=ft.border.all(1, ft.colors.BLACK)
                    )
                )
            cuerpo_calendario.controls.append(row)

        return ft.Column(
            [
                ft.Text("Calendario de Ocupación", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("Vista rápida de la disponibilidad de habitaciones."),
                ft.Divider(),
                header_row,
                ft.Divider(),
                cuerpo_calendario,
            ],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True
        )
