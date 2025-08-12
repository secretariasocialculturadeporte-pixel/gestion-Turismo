# turismo_app/core/assets_manager.py
import flet as ft

# === RUTAS A ASSETS ===
# Asume que tienes una carpeta 'assets' en la raíz de 'turismo_app'
BASE_ASSETS_PATH = "/assets"  # Flet sirve desde /assets por defecto si está configurado en ft.app()

# Iconos de aplicación
LOGO_APP_LOGIN = f"{BASE_ASSETS_PATH}/icons/logo_app_login_128.png"  # Ejemplo, necesitas crear este ícono
LOGO_APP_NAVBAR = f"{BASE_ASSETS_PATH}/icons/logo_app_navbar_64.png"  # Ejemplo
ICONO_TURISMO_DEFAULT = ft.icons.LOCATION_CITY_ROUNDED  # Icono por defecto para el sistema

# Imágenes Generales / Marcadores de posición
IMG_HOME_BACKGROUND = f"{BASE_ASSETS_PATH}/images/home_background_turismo_regional.jpg"  # Ejemplo
IMG_PLACEHOLDER_ATRACTIVO = f"{BASE_ASSETS_PATH}/images/placeholder_atractivo.png"
IMG_PLACEHOLDER_EMPRESA = f"{BASE_ASSETS_PATH}/images/placeholder_empresa.png"

# === PALETA DE COLORES SEMÁNTICA (Complementaria al Tema Flet) ===
# Puedes definir colores específicos si el tema no cubre todos tus casos de uso.
COLOR_TEXTO_TITULO_SECCION = ft.colors.PRIMARY  # Basado en el tema actual
COLOR_TEXTO_SUBTITULO_SECCION = ft.colors.SECONDARY
COLOR_BOTON_EXITO_BG = ft.colors.GREEN_ACCENT_700
COLOR_BOTON_EXITO_FG = ft.colors.WHITE
COLOR_BOTON_ERROR_BG = ft.colors.RED_ACCENT_700
COLOR_BOTON_ERROR_FG = ft.colors.WHITE
COLOR_BADGE_INFO = ft.colors.BLUE_GREY_100
COLOR_TEXTO_BADGE_INFO = ft.colors.BLUE_GREY_800

# === CONSTANTES DE UI ===
PADDING_SECCION_FORMULARIO = ft.padding.symmetric(horizontal=20, vertical=15)
ELEVATION_CARD_FORMULARIO = 2
BORDER_RADIUS_CONTROLES = 8
BORDER_TABLA_HISTORIAL = ft.border.all(1.5, ft.colors.with_opacity(0.3, ft.colors.OUTLINE_VARIANT))

# === Textos Fijos (Si hay muchos y quieres centralizarlos) ===
TEXTO_BOTON_GUARDAR = "Guardar Cambios"
TEXTO_BOTON_NUEVO = "Crear Nuevo"
TEXTO_CONFIRMACION_ELIMINAR = "¿Está seguro de que desea eliminar este elemento? Esta acción no se puede deshacer."

# === Funciones Helper para Assets (Opcional) ===
def get_icon(icon_name_str: str, default_icon = ft.icons.HELP_OUTLINE) -> str:
    """
    Retorna el objeto ft.icons si el string es un nombre de icono válido.
    Esto es útil si guardas nombres de icono como string en tus constantes de metodología.
    """
    return getattr(ft.icons, icon_name_str.upper(), default_icon)

# Ejemplo de cómo usarlo en otras vistas:
# from turismo_app.core import assets_manager as am
# ...
# ft.Image(src=am.LOGO_APP_LOGIN)
# ft.ElevatedButton(style=ft.ButtonStyle(bgcolor=am.COLOR_BOTON_EXITO_BG))
# ft.Icon(am.get_icon("ACCOUNT_BALANCE_WALLET_OUTLINED"))
