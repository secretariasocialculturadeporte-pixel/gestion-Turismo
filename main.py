import flet as ft
import logging

# --- Importar las vistas de la aplicación ---
from turismo_app.views.login_view import LoginView
from turismo_app.views.home_view import HomeView
from turismo_app.views.admin.admin_dashboard_view import AdminDashboardView
from turismo_app.views.ciudadano.ciudadano_turismo_view import CiudadanoTurismoView
from turismo_app.views.ciudadano.ciudadano_empleo_view import CiudadanoEmpleoView
from turismo_app.views.ciudadano.ciudadano_feedback_view import CiudadanoFeedbackView
from turismo_app.views.admin.gestion_contenido.admin_empresas_view import AdminEmpresasView
from turismo_app.views.chatbot_view import ChatbotView
from turismo_app.views.empresa.empresa_dashboard_view import EmpresaDashboardView
from turismo_app.views.empresa.empresa_gestion_productos_view import EmpresaGestionProductosView
from turismo_app.views.empresa.empresa_registro_clientes_view import EmpresaRegistroClientesView
from turismo_app.views.empresa.restaurante_admin_panel_view import RestauranteAdminPanelView
from turismo_app.views.empresa.restaurante_gestion_menu_view import RestauranteGestionMenuView
from turismo_app.views.empresa.restaurante_gestion_mesas_view import RestauranteGestionMesasView
from turismo_app.views.empresa.restaurante_tpv_view import RestauranteTPVView
from turismo_app.views.empresa.restaurante_kds_view import RestauranteKDSView
from turismo_app.views.empresa.restaurante_recepcion_view import RestauranteRecepcionView
from turismo_app.views.empresa.agencia_gestion_paquetes_view import AgenciaGestionPaquetesView
from turismo_app.views.empresa.agencia_gestion_reservas_view import AgenciaGestionReservasView
from turismo_app.views.empresa.gestion_recursos_view import GestionRecursosView
from turismo_app.views.guia.guia_perfil_view import GuiaPerfilView
from turismo_app.views.guia.guia_reservas_view import GuiaReservasView
from turismo_app.views.ciudadano.ciudadano_guias_view import CiudadanoGuiasView
from turismo_app.views.empresa.gestion_costos_view import GestionCostosView
from turismo_app.views.empresa.gestion_reglas_precios_view import GestionReglasPreciosView
from turismo_app.views.shared.calendario_disponibilidad_view import CalendarioDisponibilidadView


# --- Configuración del Logging ---
logging.basicConfig(level=logging.INFO)

# --- Definición de Rutas ---
# Es una buena práctica tener las rutas centralizadas
ROUTE_HOME = "/"
ROUTE_LOGIN = "/auth/login"
ROUTE_ADMIN_DASHBOARD = "/admin/dashboard"
ROUTE_ADMIN_EMPRESAS = "/admin/empresas"
ROUTE_CIUDADANO_TURISMO = "/ciudadano/turismo"
ROUTE_CIUDADANO_EMPLEO = "/ciudadano/empleo"
ROUTE_CIUDADANO_FEEDBACK = "/ciudadano/feedback"
ROUTE_CHATBOT = "/chatbot"
ROUTE_EMPRESA_DASHBOARD = "/empresa/dashboard"
ROUTE_EMPRESA_PRODUCTOS = "/empresa/productos"
ROUTE_EMPRESA_CLIENTES = "/empresa/clientes"
ROUTE_HOTEL_HABITACIONES = "/empresa/hotel/habitaciones"
ROUTE_HOTEL_RESERVAS = "/empresa/hotel/reservas"
ROUTE_HOTEL_CALENDARIO = "/empresa/hotel/calendario"
ROUTE_RESTAURANTE_ADMIN = "/empresa/restaurante/admin"
ROUTE_RESTAURANTE_MENU = "/empresa/restaurante/menu"
ROUTE_RESTAURANTE_MESAS = "/empresa/restaurante/mesas"
ROUTE_RESTAURANTE_TPV = "/empresa/restaurante/tpv"
ROUTE_RESTAURANTE_KDS = "/empresa/restaurante/kds"
ROUTE_RESTAURANTE_RECEPCION = "/empresa/restaurante/recepcion"
ROUTE_AGENCIA_PAQUETES = "/empresa/agencia/paquetes"
ROUTE_AGENCIA_RESERVAS = "/empresa/agencia/reservas"
ROUTE_EMPRESA_INVENTARIO = "/empresa/inventario"
ROUTE_EMPRESA_CALENDARIO = "/empresa/calendario"
ROUTE_EMPRESA_RECURSOS = "/empresa/recursos"
ROUTE_EMPRESA_COSTOS = "/empresa/costos"
ROUTE_EMPRESA_PRECIOS = "/empresa/precios"
ROUTE_GUIA_PERFIL = "/guia/perfil"
ROUTE_GUIA_RESERVAS = "/guia/reservas"
ROUTE_CIUDADANO_GUIAS = "/ciudadano/guias"


class AppState:
    """Clase simple para mantener el estado de la navegación."""
    def __init__(self):
        self.app_bar = None
        self.nav_rail = None
        self.main_content = None

def main(page: ft.Page):
    """Función principal que se ejecuta al iniciar la aplicación Flet."""

    page.title = "Sistema de Gestión Turística Territorial"

    # --- Configuración del Tema ---
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE_GREY,
        use_material3=True,
    )

    # El objeto de estado para esta sesión
    app_state = AppState()

    # --- Lógica de Autenticación y Sesión ---
    def on_login_success(user_data: dict):
        """Callback que se ejecuta cuando el login es exitoso."""
        logging.info(f"Callback on_login_success recibido. Usuario: {user_data.get('nombre_usuario')}, Rol: {user_data.get('rol')}")
        # Guardar datos del usuario en la sesión de la página
        for key, value in user_data.items():
            page.session.set(f"user_{key}", value)
            logging.info(f"Guardando en sesión: user_{key} = {value}")

        # Redirigir al dashboard correspondiente
        if user_data.get('rol') in ["SuperAdmin", "AdminMunicipal", "AdminDepartamental"]:
            page.go(ROUTE_ADMIN_DASHBOARD)
        elif user_data.get('rol') == "PropietarioEmpresa":
            page.go(ROUTE_EMPRESA_DASHBOARD)
        else:
            page.go(ROUTE_HOME)

    def on_logout(e=None):
        """Limpia la sesión y redirige al login."""
        logging.info("Cerrando sesión de usuario.")
        # Limpiar todas las claves de sesión relacionadas con el usuario
        keys_to_clear = [key for key in page.session.get_keys() if key.startswith("user_")]
        for key in keys_to_clear:
            page.session.remove(key)
        page.go(ROUTE_LOGIN)

    # --- Definición de las Vistas/Rutas ---
    def route_change(route_event: ft.RouteChangeEvent):
        """Manejador de cambio de ruta."""
        logging.info(f"Cambiando a la ruta: {route_event.route}")

        # Proteger rutas que requieren autenticación
        is_authenticated = page.session.get("user_id") is not None
        user_rol = page.session.get("user_rol")
        is_admin = user_rol in ["SuperAdmin", "AdminMunicipal", "AdminDepartamental"]
        is_propietario = user_rol == "PropietarioEmpresa"

        admin_routes = [ROUTE_ADMIN_DASHBOARD, ROUTE_ADMIN_EMPRESAS]
        empresa_routes = [ROUTE_EMPRESA_DASHBOARD, ROUTE_EMPRESA_PRODUCTOS, ROUTE_EMPRESA_CLIENTES]

        if route_event.route in admin_routes and not (is_authenticated and is_admin):
            page.go(ROUTE_LOGIN)
            return

        if route_event.route in empresa_routes and not (is_authenticated and is_propietario):
            page.go(ROUTE_LOGIN)
            return

        # Limpiar la vista anterior
        page.views.clear()

        # --- Vistas Públicas / Comunes ---
        if route_event.route == ROUTE_LOGIN:
            page.views.append(
                ft.View(
                    route=ROUTE_LOGIN,
                    controls=[LoginView(page, on_login_success=on_login_success)],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    padding=0
                )
            )
        else:
            # --- Vistas que usan la estructura principal (AppBar, NavRail) ---

            # Crear la barra de navegación lateral (NavRail)
            nav_rail_destinations = [
                ft.NavigationRailDestination(icon=ft.icons.HOME_OUTLINED, selected_icon=ft.icons.HOME, label="Inicio"),
                ft.NavigationRailDestination(icon=ft.icons.TRAVEL_EXPLORE_OUTLINED, selected_icon=ft.icons.TRAVEL_EXPLORE, label="Turismo"),
                ft.NavigationRailDestination(icon=ft.icons.WORK_OUTLINE, selected_icon=ft.icons.WORK, label="Empleo"),
                ft.NavigationRailDestination(icon=ft.icons.FEEDBACK_OUTLINED, selected_icon=ft.icons.FEEDBACK, label="Feedback"),
                ft.NavigationRailDestination(icon=ft.icons.ASSISTANT_OUTLINED, selected_icon=ft.icons.ASSISTANT, label="Asistente"),
                ft.NavigationRailDestination(icon=ft.icons.PERSON_SEARCH_OUTLINED, selected_icon=ft.icons.PERSON_SEARCH, label="Guías"),
            ]

            if is_admin:
                nav_rail_destinations.append(
                    ft.NavigationRailDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD, label="Admin")
                )
            if is_propietario:
                nav_rail_destinations.append(
                    ft.NavigationRailDestination(icon=ft.icons.BUSINESS_OUTLINED, selected_icon=ft.icons.BUSINESS, label="Mi Empresa")
                )

            def on_nav_rail_change(e):
                index = e.control.selected_index
                if index == 0: page.go(ROUTE_HOME)
                elif index == 1: page.go(ROUTE_CIUDADANO_TURISMO)
                elif index == 2: page.go(ROUTE_CIUDADANO_EMPLEO)
                elif index == 3: page.go(ROUTE_CIUDADANO_FEEDBACK)
                elif index == 4: page.go(ROUTE_CHATBOT)
                elif index == 5: page.go(ROUTE_CIUDADANO_GUIAS)
                elif index == 6:
                    if is_admin: page.go(ROUTE_ADMIN_DASHBOARD)
                    elif is_propietario: page.go(ROUTE_EMPRESA_DASHBOARD)


            # Determinar el índice seleccionado para el NavRail
            route_to_nav_index = {
                ROUTE_HOME: 0,
                ROUTE_CIUDADANO_TURISMO: 1,
                ROUTE_CIUDADANO_EMPLEO: 2,
                ROUTE_CIUDADANO_FEEDBACK: 3,
                ROUTE_CHATBOT: 4,
                ROUTE_CIUDADANO_GUIAS: 5,
                ROUTE_ADMIN_DASHBOARD: 6,
                ROUTE_ADMIN_EMPRESAS: 6,
                ROUTE_EMPRESA_DASHBOARD: 6,
                ROUTE_EMPRESA_PRODUCTOS: 6,
                ROUTE_EMPRESA_CLIENTES: 6,
                ROUTE_GUIA_PERFIL: 6,
                ROUTE_GUIA_RESERVAS: 6,
            }

            app_state.nav_rail = ft.NavigationRail(
                selected_index=route_to_nav_index.get(page.route, 0),
                label_type=ft.NavigationRailLabelType.ALL,
                destinations=nav_rail_destinations,
                on_change=on_nav_rail_change,
                group_alignment=-0.9
            )

            # Crear la barra de aplicación superior (AppBar)
            app_state.app_bar = ft.AppBar(
                title=ft.Text("Portal Turístico"),
                center_title=False,
                bgcolor=ft.colors.SURFACE_VARIANT,
                actions=[
                    ft.IconButton(ft.icons.BRIGHTNESS_4_OUTLINED, on_click=lambda e: setattr(page, 'theme_mode', 'dark' if page.theme_mode == 'light' else 'light') or page.update()),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(text="Cerrar Sesión", icon=ft.icons.LOGOUT, on_click=on_logout) if is_authenticated else ft.PopupMenuItem(text="Iniciar Sesión", icon=ft.icons.LOGIN, on_click=lambda _: page.go(ROUTE_LOGIN))
                        ]
                    )
                ]
            )

            # --- Contenido Principal (segun la ruta) ---
            view_classes = {
                ROUTE_HOME: HomeView,
                ROUTE_ADMIN_DASHBOARD: AdminDashboardView,
                ROUTE_ADMIN_EMPRESAS: AdminEmpresasView,
                ROUTE_CIUDADANO_TURISMO: CiudadanoTurismoView,
                ROUTE_CIUDADANO_EMPLEO: CiudadanoEmpleoView,
                ROUTE_CIUDADANO_FEEDBACK: CiudadanoFeedbackView,
                ROUTE_CHATBOT: ChatbotView,
                ROUTE_EMPRESA_DASHBOARD: EmpresaDashboardView,
                ROUTE_EMPRESA_PRODUCTOS: EmpresaGestionProductosView,
                ROUTE_EMPRESA_CLIENTES: EmpresaRegistroClientesView,
                ROUTE_EMPRESA_RECURSOS: GestionRecursosView,
                ROUTE_RESTAURANTE_ADMIN: RestauranteAdminPanelView,
                ROUTE_RESTAURANTE_MENU: RestauranteGestionMenuView,
                ROUTE_RESTAURANTE_MESAS: RestauranteGestionMesasView,
                ROUTE_RESTAURANTE_TPV: RestauranteTPVView,
                ROUTE_RESTAURANTE_KDS: RestauranteKDSView,
                ROUTE_RESTAURANTE_RECEPCION: RestauranteRecepcionView,
                ROUTE_AGENCIA_PAQUETES: AgenciaGestionPaquetesView,
                ROUTE_AGENCIA_RESERVAS: AgenciaGestionReservasView,
                ROUTE_EMPRESA_COSTOS: GestionCostosView,
                ROUTE_EMPRESA_PRECIOS: GestionReglasPreciosView,
                ROUTE_EMPRESA_CALENDARIO: CalendarioDisponibilidadView,
                ROUTE_GUIA_PERFIL: GuiaPerfilView,
                ROUTE_GUIA_RESERVAS: GuiaReservasView,
                ROUTE_CIUDADANO_GUIAS: CiudadanoGuiasView,
            }

            view_class = view_classes.get(page.route)
            if view_class:
                # Instanciar la clase y llamar a build()
                app_state.main_content = view_class(page).build()
            else:
                app_state.main_content = ft.Text(f"Ruta no encontrada o vista no implementada: {page.route}")


            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        app_state.app_bar,
                        ft.Row(
                            [
                                app_state.nav_rail,
                                ft.VerticalDivider(width=1),
                                ft.Column([app_state.main_content], expand=True, scroll=ft.ScrollMode.ADAPTIVE),
                            ],
                            expand=True,
                        )
                    ],
                    padding=0
                )
            )
        page.update()

    # --- Configuración Inicial de la Página ---
    page.on_route_change = route_change

    # Iniciar en la página de login si no hay sesión, si no en el home
    if not page.session.get("user_id"):
        page.go(ROUTE_LOGIN)
    else:
        page.go(ROUTE_HOME)

# --- Punto de Entrada para Ejecutar la App ---
if __name__ == "__main__":
    import flet as ft

    ft.app(
        target=main,
        assets_dir="turismo_app/assets"
    )
