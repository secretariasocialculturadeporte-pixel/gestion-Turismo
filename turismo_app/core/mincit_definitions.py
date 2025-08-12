# turismo_app/core/mincit_definitions.py
# Archivo: mincit_definitions.py
"""
Este archivo contiene las definiciones estructurales basadas en los formatos y metodologías
del Ministerio de Comercio, Industria y Turismo (MinCIT) de Colombia.

¡IMPORTANTE! Las estructuras aquí presentes (FORMATO_MINCIT_ATRACTIVOS_REAL y METODOLOGIA_MINCIT_NDTT_REAL)
son INTERPRETACIONES o SIMULACIONES basadas en la información visual proporcionada.
El usuario/desarrollador final DEBE REEMPLAZARLAS con las definiciones exactas y completas
extraídas de los documentos oficiales del MinCIT para asegurar la precisión y validez del sistema.
"""
import flet as ft

# ========================================================================================================
# 1. FORMATO ÚNICO DE INVENTARIOS TURÍSTICOS MINCIT - ESTRUCTURA PARA EL SISTEMA
# =========================================================================================================
# - Cada clave principal en `FORMATO_MINCIT_ATRAACTIVOS_REAL` (ej. "PATRIMONIO_CULTURAL_MATERIAL")
#   debe corresponder a una de las `key` en `TIPOS_PRINCIPALES_ATRACTIVO`.
# - Dentro de cada tipo, `secciones_especificas` es una LISTA de diccionarios, cada uno
#   representando una sección del formulario.
# - Cada sección tiene "campos" (un dict) o "criterios_calidad" (una lista de dicts).
# - Para cada campo/criterio:
#   - "key_db": Nombre de columna en la tabla `atractivos_turisticos` (DEBE SER ÚNICO GLOBALMENTE si la tabla es ancha, o tener prefijos).
#   - "label": Texto visible en el formulario Flet.
#   - "tipo_flet": "TextField", "Dropdown", "Switch", "Slider", "DatePickerButton", "CheckboxGroup".
#   - "requerido": Verdadero/Falso.
#   - Propiedades específicas del tipo_flet: "options_dict", "options_list", "min", "max", "divisions",
#     "keyboard_type", "input_filter_regex", "multiline", "default_value", etc.
#   - "ayuda": Texto para información sobre herramientas.
#   - "max_puntaje": Para criterios de calidad/significado, el puntaje máximo posible.

FORMATO_MINCIT_ATRACTIVOS_REAL = {
    "TIPOS_PRINCIPALES_ATRACTIVO": {
        "PATRIMONIO_CULTURAL_MATERIAL": "Patrimonio Cultural - Material (Bienes Inmuebles y Muebles)",
        "PATRIMONIO_CULTURAL_INMATERIAL": "Patrimonio Cultural - Inmaterial (Manifestaciones, Tradiciones)",
        "FESTIVIDADES_EVENTOS": "Festividades y Eventos Programados",
        "GRUPOS_ESPECIAL_INTERES": "Grupos Étnicos y Comunidades de Especial Interés Turístico",
        "SITIOS_NATURALES": "Sitios Naturales (Paisajes, Ecosistemas, Accidentes Geográficos)",
        # AÑADE MÁS TIPOS DE FORMULARIOS ESPECIALES SEGÚN EL DOCUMENTO MINCIT
        # "REALIZACIONES_TECNICO_CIENTIFICAS": "Realizaciones Técnico-Científicas y Artísticas Contemporáneas",
        # "MUSEOS_Y_COLECCIONES": "Museos, Colecciones y Sitios de Interés Histórico/Científico",
    },
    "SECCIONES_COMUNES": {
        "GENERALIDADES_COMUNES": {
            "label": "1. Identificación y Generalidades del Atractivo",
            "icon": "FINGERPRINT",
            "expanded": True,
            "campos": {
                "nombre_atractivo": {"label": "1.1 Nombre Oficial del Atractivo*", "tipo_flet": "TextField", "requerido": True, "max_length": 250, "ayuda": "Nombre oficial o más conocido del atractivo."},
                "codigo_inventario_mincit": {"label": "Código Asignado MinCIT (si existe)", "tipo_flet": "TextField", "max_length": 50, "ayuda": "Código oficial del sistema de inventarios del Viceministerio (si ya fue inventariado)."},
                "otros_nombres_comunes": {"label": "Otros Nombres Comunes/Populares", "tipo_flet": "TextField", "max_length": 300},
                "corregimiento_vereda_localidad": {"label": "1.4 Corregimiento, Vereda o Localidad", "tipo_flet": "TextField", "max_length": 150},
                "administrador_o_propietario": {"label": "1.5 Administrador o Propietario Principal", "tipo_flet": "TextField", "max_length": 200},
                "direccion_descriptiva_ubicacion": {"label": "1.6 Dirección/Ubicación Detallada y Referencias*", "tipo_flet": "TextField", "multiline": True, "min_lines": 3, "requerido": True, "max_length": 500},
                "telefono_contacto_atractivo": {"label": "1.7 Teléfono(s) de Contacto del Atractivo", "tipo_flet": "TextField", "max_length": 100},
                "email_contacto_atractivo": {"label": "Email de Contacto del Atractivo", "tipo_flet": "TextField", "keyboard_type": "email", "max_length": 150},
                "pagina_web_atractivo": {"label": "Página Web o Red Social Principal", "tipo_flet": "TextField", "keyboard_type": "url", "max_length": 200},
                "distancia_cabecera_km": {"label": "1.8 Distancia desde Cabecera Mpal. (Km)", "tipo_flet": "TextField", "keyboard_type": "number", "input_filter_regex": r"^\d{0,4}(\.\d{0,1})?$", "ayuda": "Ej: 10.5 Km"},
                "tiempo_recorrido_desde_cabecera": {"label": "Tiempo de Recorrido desde Cabecera (Ej: 30 min en carro)", "tipo_flet": "TextField", "max_length": 100},
                "tipos_acceso_principal": {"label": "1.9 Tipo(s) de Acceso Principal al Atractivo*", "tipo_flet": "CheckboxGroup", "options": ["Terrestre (Carretera Pavimentada)", "Terrestre (Carretera Afirmada/Vía destapada)", "Terrestre (Sendero Peatonal)", "Acuático/Marítimo", "Fluvial", "Férreo", "Aéreo (Aeropuerto/Helipuerto cercano)"], "requerido": True, "ayuda": "Marque todos los que apliquen."},
                "estado_vias_acceso_terrestre": {"label": "Estado de Vías de Acceso Terrestre", "tipo_flet": "Dropdown", "options_dict": {"BUENO": "Bueno", "REGULAR": "Regular", "MALO": "Malo", "VARIABLE_SEGUN_CLIMA": "Variable según clima", "NO_APLICA": "No Aplica Terrestre"}, "ayuda": "Si el acceso principal es terrestre."},
                "indicaciones_llegada_detalladas": {"label": "1.11 Indicaciones Detalladas para el Acceso y Medios de Transporte", "tipo_flet": "TextField", "multiline": True, "min_lines": 3, "max_length": 1000},
                "latitud_grados_dec": {"label": "Latitud Geográfica (Grados Decimales)", "tipo_flet": "TextField", "keyboard_type": "number", "input_filter_regex": r"^-?\d{1,2}(\.\d{1,7})?$", "ayuda": "Ej: 4.570868. Usar punto decimal."},
                "longitud_grados_dec": {"label": "Longitud Geográfica (Grados Decimales)", "tipo_flet": "TextField", "keyboard_type": "number", "input_filter_regex": r"^-?\d{1,3}(\.\d{1,7})?$", "ayuda": "Ej: -74.297333. Usar punto decimal."},
                "altitud_msnm": {"label": "Altitud (msnm)", "tipo_flet": "TextField", "keyboard_type": "number", "input_filter_regex": r"^\d{0,4}$"},
            }
        },
        "PUNTAJES_SIGNIFICADO_COMUNES": {
            "label": "3.2 Calificación: Significado y Representatividad",
            "icon": "FLAG_CIRCLE_OUTLINED",
            "criterios_significado": [
                {"key_db": "significado_local", "label": "Local (Hasta 6 pts)", "tipo_flet": "Slider", "min": 0, "max": 6, "divisions": 6, "default_value": 0, "max_puntaje_criterio": 6, "ayuda": "Importancia y reconocimiento a nivel municipal/comunitario."},
                {"key_db": "significado_regional", "label": "Regional (Hasta 12 pts)", "tipo_flet": "Slider", "min": 0, "max": 12, "divisions": 12, "default_value": 0, "max_puntaje_criterio": 12, "ayuda": "Reconocimiento e influencia a nivel subregional o departamental."},
                {"key_db": "significado_nacional", "label": "Nacional (Hasta 18 pts)", "tipo_flet": "Slider", "min": 0, "max": 18, "divisions": 18, "default_value": 0, "max_puntaje_criterio": 18, "ayuda": "Reconocimiento, unicidad o importancia a nivel de país."},
                {"key_db": "significado_internacional", "label": "Internacional (Hasta 30 pts)", "tipo_flet": "Slider", "min": 0, "max": 30, "divisions": 15, "default_value": 0, "max_puntaje_criterio": 30, "ayuda": "Reconocimiento, unicidad o demanda a nivel mundial (ej. Patrimonio Humanidad)."},
            ],
            "subtotal_key_db": "subtotal_significado_final", # Columna en BD para este subtotal
            "max_total_significado": 66
        },
        # ... (SECCIÓN DE DILIGENCIAMIENTO COMÚN) ...
    },
    # --- SECCIONES ESPECÍFICAS POR TIPO DE ATRACTIVO ---
    "PATRIMONIO_CULTURAL_MATERIAL": {
        # ... (definición COMPLETA como la esbozamos antes, con CADA CAMPO y CRITERIO DE CALIDAD) ...
        "secciones_especificas": [
            {
                "key_seccion": "CARACTERISTICAS_PATMAT",
                "label": "2.2 Características Específicas (Pat. Material)",
                "icon": "ACCOUNT_BALANCE",
                "expanded": True,
                "campos": {
                    # Debes completar esto con los campos REALES del formulario MinCIT
                    "descripcion_patmat_detallada": {"label": "Descripción del Bien (Tipología, Estilo, Época, Autor, Materiales, Técnica Constructiva, Estado de Componentes, Uso Actual)*", "tipo_flet": "TextField", "multiline": True, "min_lines": 7, "requerido": True, "ayuda": "Sea lo más exhaustivo posible."},
                    # ...
                }
            },
            {
                "key_seccion": "CALIDAD_PATMAT",
                "label": "3.1 Puntajes de Calidad (Pat. Material)",
                "icon": "STAR_RATE_OUTLINED",
                "criterios_calidad": [
                    # DEBES USAR LOS CRITERIOS Y PUNTAJES EXACTOS DEL FORMULARIO MINCIT
                    {"key_db": "cal_patmat_estado_conserv", "label": "Estado de Conservación", "max_puntaje_criterio": 21, "tipo_flet": "Slider", "min": 0, "divisions": 21},
                    {"key_db": "cal_patmat_constitucion_bien", "label": "Constitución del Bien", "max_puntaje_criterio": 21, "tipo_flet": "Slider", "min": 0, "divisions": 21},
                    {"key_db": "cal_patmat_representatividad", "label": "Representatividad General", "max_puntaje_criterio": 28, "tipo_flet": "Slider", "min": 0, "divisions": 28},
                ],
                "subtotal_key_db": "subtotal_calidad_patmat_final"
            }
            # ... Agregue aquí OTRAS SECCIONES ESPECÍFICAS DEL FORMULARIO DE PATRIMONIO MATERIAL
            # (Ej: Servicios Turísticos Asociados, Normatividad, Plan de Manejo, etc.)
        ]
    },
    # --- REPITE LA ESTRUCTURA PARA CADA TIPO EN "TIPOS_PRINCIPALES_ATRACTIVO" ---
    "SITIOS_NATURALES": {
        "secciones_especificas": [
            # ... Sección de Características Específicas para Sitios Naturales (TODOS SUS CAMPOS)
            # ... Sección de Criterios de Calidad para Sitios Naturales (TODOS SUS CRITERIOS Y PUNTAJES MAX)
        ]
    },
    # ... PATRIMONIO_CULTURAL_INMATERIAL, FESTIVIDADES_EVENTOS, GRUPOS_ESPECIAL_INTERES...
}

# =======================================================================================================
# METODOLOGÍA NDTT MINCIT - ESTRUCTURA PARA EL SISTEMA
# =======================================================================================================
METODOLOGIA_MINCIT_NDTT_REAL = {
    # ... (TU ESTRUCTURA COMPLETA Y REAL DE LOS 14 EJES, con indicadores, tipo_flet,
    # options_dict/rangos_puntaje, puntaje_max_indicador,y ponderacion_dimension
    # TAL COMO LA COMPLETARÍAS BASADO EN LAS IMÁGENES Y EL DOCUMENTO OFICIAL)
    ...
}

ICONOS_EJES_NDTT = {
    # Opcional, para la UI del formulario de diagnóstico
    # ... (Como lo tenías, con una clave por cada EJE)
}
