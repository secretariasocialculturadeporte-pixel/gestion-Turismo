import flet as ft
from turismo_app.database import db_manager

class ReportesConsolidadosView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.current_user_role = page.session.get("user_rol")
        self.codigo_departamento_admin = page.session.get("user_codigo_departamento")

    def did_mount(self):
        # En una implementación real, aquí se cargarían los datos consolidados
        # basados en el rol y el código de depto/nación del usuario.
        pass

    def build(self):
        # Lógica para restringir acceso si no es un rol adecuado
        if self.current_user_role not in ["SuperAdmin", "AdminDepartamental"]: # Ejemplo
             return ft.Container(
                content=ft.Text("Acceso denegado. Se requiere un rol de mayor nivel.", color=ft.colors.ERROR),
                padding=50
            )

        title = ft.Text("Reportes Consolidados", style=ft.TextThemeStyle.HEADLINE_MEDIUM)

        info_text = ""
        if self.current_user_role == "AdminDepartamental":
            info_text = f"Mostrando datos para el departamento: {self.codigo_departamento_admin}"
        elif self.current_user_role == "SuperAdmin":
            info_text = "Mostrando datos a nivel nacional."

        placeholder_content = ft.Column(
            [
                ft.Text("Esta sección mostrará reportes agregados a nivel departamental o nacional.", size=16),
                ft.Text("Incluirá comparativas entre municipios/departamentos y KPIs de alto nivel.", italic=True, color=ft.colors.OUTLINE),
                ft.Divider(height=20),
                ft.Text("Ejemplos de Gráficos a Implementar:"),
                ft.Text("- Ranking de municipios por número de atractivos."),
                ft.Text("- Comparativa de formalidad de empresas por municipio."),
                ft.Text("- Evolución de vacantes de empleo a nivel departamental."),
            ],
            spacing=10
        )

        return ft.Container(
            content=ft.Column(
                [
                    title,
                    ft.Text(info_text, style=ft.TextThemeStyle.BODY_LARGE),
                    ft.Divider(),
                    placeholder_content,
                ],
                spacing=15,
                scroll=ft.ScrollMode.ADAPTIVE,
            ),
            padding=20
        )
