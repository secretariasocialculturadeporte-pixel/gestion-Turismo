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
    """
    Lista, filtra, ordena y pagina las empresas para el panel de administración.
    Devuelve una tupla con la lista de resultados y el conteo total de items filtrados.
    """
    base_query = """
        SELECT e.*, m.nombre_municipio
        FROM empresas_prestadores_turisticos e
        JOIN municipios m ON e.codigo_municipio = m.codigo_municipio
    """
    count_query = "SELECT COUNT(*) FROM empresas_prestadores_turisticos e"

    where_clauses = []
    params = {}

    if filtros.get("codigo_municipio"):
        where_clauses.append("e.codigo_municipio = :codigo_municipio")
        params["codigo_municipio"] = filtros["codigo_municipio"]

    if filtros.get("razon_social__icontains"):
        where_clauses.append("e.razon_social_o_nombre_comercial LIKE :razon_social")
        params["razon_social"] = f"%{filtros['razon_social__icontains']}%"

    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)
        base_query += where_sql
        count_query += where_sql

    # Ordenamiento
    if orden:
        col, direccion = list(orden.items())[0]
        # Sanitización simple para evitar SQL injection en ORDER BY
        allowed_cols = ["razon_social_o_nombre_comercial", "aprobada_publicar", "activo"]
        if col in allowed_cols and direccion in ["ASC", "DESC"]:
            base_query += f" ORDER BY {col} {direccion}"

    # Paginación
    base_query += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Obtener el total de items
            total_items = cursor.execute(count_query, params).fetchone()[0]

            # Obtener los resultados paginados
            resultados = cursor.execute(base_query, params).fetchall()

            return [dict(row) for row in resultados], total_items
    except sqlite3.Error as e:
        logger.error(f"Error al listar empresas paginado: {e}", exc_info=True)
        return [], 0

def obtener_empresa_por_id(empresa_id: int) -> dict | None:
    """Obtiene una empresa por su ID."""
    try:
        with get_db_connection() as conn:
            emp = conn.execute("SELECT * FROM empresas_prestadores_turisticos WHERE id_empresa = ?", (empresa_id,)).fetchone()
            return dict(emp) if emp else None
    except sqlite3.Error as e:
        logger.error(f"Error al obtener empresa ID {empresa_id}: {e}", exc_info=True)
        return None

def crear_o_actualizar_empresa(datos: dict, empresa_id: int | None = None) -> int | None:
    """Crea o actualiza un registro de empresa."""
    if empresa_id: # Actualizar
        sql = """
            UPDATE empresas_prestadores_turisticos SET
            razon_social_o_nombre_comercial = :razon_social_o_nombre_comercial,
            nit = :nit, tipo_prestador = :tipo_prestador, tipo_prestador_otro = :tipo_prestador_otro,
            es_formal = :es_formal, rnt = :rnt, descripcion_servicios = :descripcion_servicios,
            direccion_principal = :direccion_principal, telefonos_contacto = :telefonos_contacto,
            email_contacto = :email_contacto, pagina_web = :pagina_web, aprobada_publicar = :aprobada_publicar,
            activo = :activo, fecha_ultima_actualizacion = :fecha_ultima_actualizacion
            WHERE id_empresa = :id_empresa
        """
        datos['id_empresa'] = empresa_id
    else: # Crear
        sql = """
            INSERT INTO empresas_prestadores_turisticos (
            razon_social_o_nombre_comercial, nit, tipo_prestador, tipo_prestador_otro, es_formal, rnt,
            descripcion_servicios, direccion_principal, telefonos_contacto, email_contacto, pagina_web,
            aprobada_publicar, activo, codigo_municipio, registrada_por_usuario_id, fecha_ultima_actualizacion
            ) VALUES (
            :razon_social_o_nombre_comercial, :nit, :tipo_prestador, :tipo_prestador_otro, :es_formal, :rnt,
            :descripcion_servicios, :direccion_principal, :telefonos_contacto, :email_contacto, :pagina_web,
            :aprobada_publicar, :activo, :codigo_municipio, :registrada_por_usuario_id, :fecha_ultima_actualizacion
            )
        """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, datos)
            conn.commit()
            return empresa_id if empresa_id else cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error al crear/actualizar empresa: {e}", exc_info=True)
        return None


# --- PLACEHOLDER para otras funciones ---
def obtener_atractivo_por_id(atractivo_id: int) -> dict | None:
    # TODO: Implementar
    logger.warning("Función 'obtener_atractivo_por_id' no implementada.")
    return {"id": atractivo_id, "nombre_atractivo": f"Atractivo de Prueba {atractivo_id}", "codigo_municipio": "05360"}

def crear_valoracion_destino(datos: dict) -> int | None:
    # TODO: Implementar
    logger.warning("Función 'crear_valoracion_destino' no implementada.")
    return 12345

def crear_valoracion_atractivo(datos: dict) -> int | None:
    # TODO: Implementar
    logger.warning("Función 'crear_valoracion_atractivo' no implementada.")
    return 67890
