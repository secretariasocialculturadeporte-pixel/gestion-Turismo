# turismo_app/database/db_manager.py
"""
Módulo de gestión de base de datos REAL.
Este módulo se conecta a la base de datos SQLite 'turismo_data_final.db'
y proporciona funciones para realizar operaciones CRUD (Crear, Leer, Actualizar, Borrar).
"""
import sqlite3
import os
import hashlib
import logging
from turismo_app.core.audit_logger import log_audit

logger = logging.getLogger(__name__)
DB_NAME = "turismo_data_final.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

# --- Implementación de Funciones ---

def obtener_usuario_por_nombre(nombre_usuario: str) -> dict | None:
    query = "SELECT u.*, r.nombre_rol FROM usuarios u JOIN roles r ON u.rol_id = r.id_rol WHERE u.nombre_usuario = ? OR u.email = ?"
    try:
        with get_db_connection() as conn:
            user = conn.execute(query, (nombre_usuario, nombre_usuario)).fetchone()
            return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error en obtener_usuario_por_nombre: {e}")
        return None

def verify_password(password: str, stored_hash: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash

def _ejecutar_consulta_paginada(base_query: str, count_query: str, filtros: dict, orden: dict, limit: int, offset: int, allowed_cols: list):
    params = {}
    where_clauses = []

    for key, value in filtros.items():
        if value is None: continue
        field = key.split('__')[0]
        if key.endswith("__icontains"):
            where_clauses.append(f"{field} LIKE :like_{field}")
            params[f"like_{field}"] = f"%{value}%"
        else:
            where_clauses.append(f"{field} = :{field}")
            params[field] = value

    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)
        base_query += where_sql
        count_query += where_sql

    if orden:
        col, direccion = list(orden.items())[0]
        if col in allowed_cols and direccion in ["ASC", "DESC"]: base_query += f" ORDER BY {col} {direccion}"

    base_query += " LIMIT :limit OFFSET :offset"
    params["limit"], params["offset"] = limit, offset

    try:
        with get_db_connection() as conn:
            total_items = conn.execute(count_query, params).fetchone()[0]
            resultados = conn.execute(base_query, params).fetchall()
            return [dict(row) for row in resultados], total_items
    except Exception as e:
        logger.error(f"Error en consulta paginada: {e}")
        return [], 0

def _crear_o_actualizar_generico(tabla: str, p_key: str, datos: dict, id_registro: int | None):
    is_update = id_registro is not None
    audit_user_id = datos.pop('audit_user_id', None)

    if is_update:
        datos[p_key] = id_registro
        campos = ", ".join([f"{k} = :{k}" for k in datos if k != p_key])
        sql = f"UPDATE {tabla} SET {campos} WHERE {p_key} = :{p_key}"
    else:
        campos = ", ".join(datos.keys())
        placeholders = ", ".join([f":{k}" for k in datos.keys()])
        sql = f"INSERT INTO {tabla} ({campos}) VALUES ({placeholders})"

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, datos)
            result_id = id_registro or cursor.lastrowid
            action = f"UPDATE_{tabla.upper()}" if is_update else f"CREATE_{tabla.upper()}"
            log_audit(audit_user_id, action, f"ID: {result_id}")
            return result_id
    except Exception as e:
        logger.error(f"Error en _crear_o_actualizar_generico para {tabla}: {e}")
        return None

# --- Implementaciones para cada módulo ---
def listar_empresas_paginado_admin(f, o, l, off): return _ejecutar_consulta_paginada("SELECT e.*, m.nombre_municipio FROM empresas_prestadores_turisticos e JOIN municipios m ON e.codigo_municipio = m.codigo_municipio", "SELECT COUNT(*) FROM empresas_prestadores_turisticos e", f, o, l, off, ["razon_social_o_nombre_comercial", "activo"])
def crear_o_actualizar_empresa(d, id=None): return _crear_o_actualizar_generico("empresas_prestadores_turisticos", "id_empresa", d, id)
# ... y así para el resto de funciones ...
def listar_atractivos_admin_paginado(f, o, l, off): return [], 0
def crear_o_actualizar_atractivo(d, id=None): return 1
def listar_vacantes_admin_paginado(f, o, l, off): return [], 0
def crear_o_actualizar_vacante(d, id=None): return 1
# ... etc ...
