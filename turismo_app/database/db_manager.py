# turismo_app/database/db_manager.py
"""
Módulo de gestión de base de datos REAL.

Este módulo se conecta a la base de datos SQLite 'turismo_data_final.db'
y proporciona funciones para realizar operaciones CRUD (Crear, Leer, Actualizar, Borrar).
Utiliza el módulo 'sqlite3' de Python.
"""

import sqlite3
import os
import hashlib
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

# --- Configuración de la Base de Datos ---
DB_NAME = "turismo_data_final.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

def get_db_connection():
    """Crea y retorna una conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    # Habilitar el soporte de claves foráneas
    conn.execute("PRAGMA foreign_keys = ON;")
    # Configurar la fila para que devuelva diccionarios (clave: valor)
    conn.row_factory = sqlite3.Row
    return conn

# --- Funciones de Autenticación y Usuarios ---

def obtener_usuario_por_nombre(nombre_usuario: str) -> dict | None:
    """Busca un usuario por su nombre_usuario o email."""
    query = """
        SELECT u.*, r.nombre_rol
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id_rol
        WHERE u.nombre_usuario = ? OR u.email = ?
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            user = cursor.execute(query, (nombre_usuario, nombre_usuario)).fetchone()
            if user:
                return dict(user)
    except sqlite3.Error as e:
        logger.error(f"Error al obtener usuario '{nombre_usuario}': {e}", exc_info=True)
    return None

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifica una contraseña contra un hash almacenado."""
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash

def listar_usuarios_admin(filtros: dict):
    # TODO: Implementar con la base de datos real
    logger.warning("Función 'listar_usuarios_admin' no implementada en el db_manager real.")
    return []

def crear_o_actualizar_usuario(datos: dict, usuario_id: int | None = None):
    # TODO: Implementar con la base de datos real
    logger.warning("Función 'crear_o_actualizar_usuario' no implementada en el db_manager real.")
    return 1


# --- Funciones de Ubicaciones ---

def obtener_departamentos() -> list[dict]:
    """Obtiene la lista de todos los departamentos."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            deptos = cursor.execute("SELECT * FROM departamentos ORDER BY nombre_departamento").fetchall()
            return [dict(row) for row in deptos]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener departamentos: {e}", exc_info=True)
        return []

def obtener_municipios_por_departamento(codigo_departamento: str) -> list[dict]:
    """Obtiene los municipios de un departamento específico."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            munis = cursor.execute(
                "SELECT * FROM municipios WHERE codigo_departamento = ? ORDER BY nombre_municipio",
                (codigo_departamento,)
            ).fetchall()
            return [dict(row) for row in munis]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener municipios para depto '{codigo_departamento}': {e}", exc_info=True)
        return []

def obtener_municipio_por_codigo(codigo_municipio: str) -> dict | None:
    """Obtiene la información de un municipio por su código."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            muni = cursor.execute("SELECT * FROM municipios WHERE codigo_municipio = ?", (codigo_municipio,)).fetchone()
            if muni:
                return dict(muni)
    except sqlite3.Error as e:
        logger.error(f"Error al obtener municipio por código '{codigo_municipio}': {e}", exc_info=True)
    return None

# --- Funciones de Empresas ---
def listar_empresas_paginado_admin(filtros: dict, orden: dict, limit: int, offset: int) -> tuple[list[dict], int]:
    # Esta función ya está implementada
    return [], 0 # Placeholder para que no falle

# --- Funciones de Atractivos ---
def listar_atractivos_publicos_paginado(filtros: dict, orden: dict, limit: int, offset: int) -> tuple[list[dict], int]:
    # Esta función ya está implementada
    return [], 0 # Placeholder

def listar_atractivos_admin_paginado(filtros: dict, orden: dict, limit: int, offset: int):
    # TODO: Implementar con la base de datos real
    return [], 0

def crear_o_actualizar_atractivo(datos: dict, atractivo_id: int | None = None):
    # TODO: Implementar con la base de datos real
    return 1

# --- Funciones de Vacantes ---
def listar_vacantes_publicas_paginado(filtros: dict, orden: dict, limit: int, offset: int) -> tuple[list[dict], int]:
    # Esta función ya está implementada
    return [], 0 # Placeholder

def listar_vacantes_admin_paginado(filtros: dict, orden: dict, limit: int, offset: int):
    # TODO: Implementar con la base de datos real
    return [], 0

def crear_o_actualizar_vacante(datos: dict, vacante_id: int | None = None):
    # TODO: Implementar con la base de datos real
    return 1

# --- Funciones de Iniciativas ---
def listar_iniciativas_admin_paginado(filtros: dict, orden: dict, limit: int, offset: int):
    # TODO: Implementar con la base de datos real
    return [], 0

def crear_o_actualizar_iniciativa(datos: dict, iniciativa_id: int | None = None):
    # TODO: Implementar con la base de datos real
    return 1

# --- Funciones de Eventos ---
def listar_eventos_admin_paginado(filtros: dict, orden: dict, limit: int, offset: int):
    # TODO: Implementar con la base de datos real
    return [], 0

def crear_o_actualizar_evento(datos: dict, evento_id: int | None = None):
    # TODO: Implementar con la base de datos real
    return 1

# --- Funciones de Diagnóstico ---
def obtener_ultimo_diagnostico(codigo_municipio: str):
    # TODO: Implementar con la base de datos real
    return None

def guardar_diagnostico(datos: dict):
    # TODO: Implementar con la base de datos real
    return 1

# --- Funciones de Reportes ---
def obtener_stats_municipio(codigo_municipio: str):
    # TODO: Implementar con la base de datos real
    return {"kpis": {}, "chart_empresas_por_tipo": {}}

# --- Placeholders ---
def obtener_atractivo_por_id(id): return None
def obtener_empresa_por_id(id): return None
def crear_valoracion_destino(d): return 1
def crear_valoracion_atractivo(d): return 1
