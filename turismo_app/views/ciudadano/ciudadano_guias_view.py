import flet as ft
from turismo_app.database import db_manager

class CiudadanoGuiasView:
    def __init__(self, page: ft.Page):
        self.page = page

        # Controles de búsqueda
        self.txt_filtro_especialidad = ft.TextField(label="Buscar por especialidad")
        self.btn_buscar = ft.IconButton(icon=ft.icons.SEARCH, on_click=self._buscar_handler)

        # Contenedor para los perfiles de los guías
        self.lista_guias = ft.ListView(expand=True, spacing=10)

    def _buscar_handler(self, e):
        filtros = {"especialidades__icontains": self.txt_filtro_especialidad.value or None}
        guias = db_manager.listar_guias_publico(filtros)

        self.lista_guias.controls.clear()
        for guia in guias:
            self.lista_guias.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(guia["nombre_completo"]),
                        subtitle=ft.Text(f"Especialidades: {guia['especialidades']}\nIdiomas: {guia['idiomas']}"),
                        trailing=ft.ElevatedButton("Contactar", on_click=self._contactar_guia, data=guia["id_usuario"])
                    )
                )
            )
        self.page.update()

    def _contactar_guia(self, e):
        # Lógica para contactar o reservar un guía
        pass

    def build(self):
        self._buscar_handler(None) # Carga inicial

        busqueda = ft.Row([self.txt_filtro_especialidad, self.btn_buscar])

        return ft.Column(
            [
                ft.Text("Guías Turísticos Disponibles", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                busqueda,
                ft.Divider(),
                self.lista_guias,
            ]
        )
