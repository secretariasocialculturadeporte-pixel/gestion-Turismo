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
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

# --- Funciones de Autenticación y Usuarios ---
def obtener_usuario_por_nombre(nombre_usuario: str) -> dict | None:
    query = "SELECT u.*, r.nombre_rol FROM usuarios u JOIN roles r ON u.rol_id = r.id_rol WHERE u.nombre_usuario = ? OR u.email = ?"
    try:
        with get_db_connection() as conn:
            user = conn.execute(query, (nombre_usuario, nombre_usuario)).fetchone()
            return dict(user) if user else None
    except sqlite3.Error as e:
        logger.error(f"Error al obtener usuario '{nombre_usuario}': {e}", exc_info=True)
        return None

def verify_password(password: str, stored_hash: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash

def listar_usuarios_admin(filtros: dict) -> list[dict]:
    # Esta implementación es simple, en un caso real tendría paginación y filtros más complejos.
    try:
        with get_db_connection() as conn:
            users = conn.execute("SELECT u.*, r.nombre_rol FROM usuarios u JOIN roles r ON u.rol_id = r.id_rol ORDER BY u.nombre_completo").fetchall()
            return [dict(row) for row in users]
    except sqlite3.Error as e:
        logger.error(f"Error al listar usuarios: {e}", exc_info=True)
        return []

def crear_o_actualizar_usuario(datos: dict, usuario_id: int | None = None):
    # Asume que 'rol' es el nombre del rol, no el id.
    if usuario_id:
        sql = "UPDATE usuarios SET nombre_usuario=:nombre_usuario, nombre_completo=:nombre_completo, email=:email, rol_id=(SELECT id_rol FROM roles WHERE nombre_rol=:rol), codigo_municipio=:codigo_municipio, activo=:activo WHERE id_usuario=:id_usuario"
        datos['id_usuario'] = usuario_id
    else:
        sql = "INSERT INTO usuarios (nombre_usuario, nombre_completo, email, password_hash, rol_id, codigo_municipio, activo) VALUES (:nombre_usuario, :nombre_completo, :email, :password_hash, (SELECT id_rol FROM roles WHERE nombre_rol=:rol), :codigo_municipio, :activo)"
        datos['password_hash'] = hashlib.sha256(datos.get("password", "").encode()).hexdigest()

    # Actualizar contraseña por separado si se proporciona
    if 'password' in datos and datos['password'] and usuario_id:
        password_sql = "UPDATE usuarios SET password_hash = ? WHERE id_usuario = ?"
        with get_db_connection() as conn:
             conn.execute(password_sql, (hashlib.sha256(datos['password'].encode()).hexdigest(), usuario_id))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, datos)
            return usuario_id or cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error al crear/actualizar usuario: {e}", exc_info=True)
        return None

# --- Funciones de Ubicaciones ---
def obtener_departamentos():
    with get_db_connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM departamentos ORDER BY nombre_departamento").fetchall()]

def obtener_municipios_por_departamento(codigo_departamento: str):
    with get_db_connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM municipios WHERE codigo_departamento = ? ORDER BY nombre_municipio", (codigo_departamento,)).fetchall()]

def obtener_municipio_por_codigo(codigo_municipio: str):
    with get_db_connection() as conn:
        muni = conn.execute("SELECT * FROM municipios WHERE codigo_municipio = ?", (codigo_municipio,)).fetchone()
        return dict(muni) if muni else None

# --- Funciones Genéricas ---
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
        base_query += " WHERE " + " AND ".join(where_clauses)
        count_query += " WHERE " + " AND ".join(where_clauses)

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
    except sqlite3.Error as e:
        logger.error(f"Error en consulta paginada: {e}", exc_info=True)
        return [], 0

def _crear_o_actualizar_generico(tabla: str, p_key: str, datos: dict, id_registro: int | None):
    if id_registro:
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
            return id_registro if id_registro else cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error en _crear_o_actualizar_generico para tabla {tabla}: {e}", exc_info=True)
        return None

# --- Implementaciones Específicas ---
def listar_empresas_paginado_admin(f, o, l, off): return _ejecutar_consulta_paginada("SELECT e.*, m.nombre_municipio FROM empresas_prestadores_turisticos e JOIN municipios m ON e.codigo_municipio = m.codigo_municipio", "SELECT COUNT(*) FROM empresas_prestadores_turisticos e", f, o, l, off, ["razon_social_o_nombre_comercial", "activo"])
def listar_atractivos_admin_paginado(f, o, l, off): return _ejecutar_consulta_paginada("SELECT a.*, m.nombre_municipio FROM atractivos_turisticos a JOIN municipios m ON a.codigo_municipio = m.codigo_municipio", "SELECT COUNT(*) FROM atractivos_turisticos a", f, o, l, off, ["nombre_atractivo", "activo"])
def listar_vacantes_admin_paginado(f, o, l, off): return _ejecutar_consulta_paginada("SELECT v.*, m.nombre_municipio FROM vacantes_empleo v JOIN municipios m ON v.codigo_municipio = m.codigo_municipio", "SELECT COUNT(*) FROM vacantes_empleo v", f, o, l, off, ["titulo_vacante", "activa"])
def listar_iniciativas_admin_paginado(f, o, l, off): return _ejecutar_consulta_paginada("SELECT * FROM iniciativas_turisticas", "SELECT COUNT(*) FROM iniciativas_turisticas", f, o, l, off, ["nombre_iniciativa", "estado"])
def listar_eventos_admin_paginado(f, o, l, off): return _ejecutar_consulta_paginada("SELECT * FROM eventos_turisticos", "SELECT COUNT(*) FROM eventos_turisticos", f, o, l, off, ["nombre_evento", "fecha_inicio"])
def listar_atractivos_publicos_paginado(f, o, l, off): return listar_atractivos_admin_paginado(f.update({"aprobado_publicar": 1, "activo": 1}), o, l, off)
def listar_vacantes_publicas_paginado(f, o, l, off): return listar_vacantes_admin_paginado(f.update({"activa": 1}), o, l, off)

def crear_o_actualizar_empresa(d, id=None): return _crear_o_actualizar_generico("empresas_prestadores_turisticos", "id_empresa", d, id)
def crear_o_actualizar_atractivo(d, id=None): return _crear_o_actualizar_generico("atractivos_turisticos", "id_atractivo", d, id)
def crear_o_actualizar_vacante(d, id=None): return _crear_o_actualizar_generico("vacantes_empleo", "id_vacante", d, id)
def crear_o_actualizar_iniciativa(d, id=None): return _crear_o_actualizar_generico("iniciativas_turisticas", "id_iniciativa", d, id)
def crear_o_actualizar_evento(d, id=None): return _crear_o_actualizar_generico("eventos_turisticos", "id_evento", d, id)

def obtener_empresa_por_id(id):
    with get_db_connection() as conn:
        return dict(conn.execute("SELECT * FROM empresas_prestadores_turisticos WHERE id_empresa = ?", (id,)).fetchone())

def obtener_atractivo_por_id(id):
    with get_db_connection() as conn:
        return dict(conn.execute("SELECT * FROM atractivos_turisticos WHERE id_atractivo = ?", (id,)).fetchone())

# ... Stubs para funciones restantes ...
def guardar_diagnostico(d): logger.warning("Función 'guardar_diagnostico' no implementada en el db_manager real."); return 1
def obtener_stats_municipio(codigo_municipio: str): return {"kpis": {}, "chart_empresas_por_tipo": {}}
def listar_entidades_educativas(f): return []
def crear_o_actualizar_entidad_educativa(d, id=None): return 1
def listar_indicadores(f): return []
def guardar_indicador(d): return 1
def crear_valoracion_destino(d): return 1
def crear_valoracion_atractivo(d): return 1
def obtener_ultimo_diagnostico(codigo_municipio: str): return None
