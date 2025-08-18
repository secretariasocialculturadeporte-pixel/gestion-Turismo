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

def obtener_empresa_por_id(empresa_id: int):
    try:
        with get_db_connection() as conn:
            empresa = conn.execute("SELECT * FROM empresas_prestadores_turisticos WHERE id_empresa = ?", (empresa_id,)).fetchone()
            return dict(empresa) if empresa else None
    except Exception as e:
        logger.error(f"Error en obtener_empresa_por_id: {e}")
        return None
# --- Gestión de Productos/Eventos por Empresa ---
def listar_productos_eventos_por_empresa_paginado(filtros: dict, orden: dict, limit: int, offset: int):
    base_query = "SELECT * FROM productos_eventos_empresa"
    count_query = "SELECT COUNT(*) FROM productos_eventos_empresa"
    allowed_cols = ["nombre_producto_evento", "tipo_oferta", "fecha_inicio", "activo"]
    return _ejecutar_consulta_paginada(base_query, count_query, filtros, orden, limit, offset, allowed_cols)

def crear_o_actualizar_producto_evento(datos: dict, producto_id: int | None = None):
    return _crear_o_actualizar_generico("productos_eventos_empresa", "id_producto_evento", datos, producto_id)

def obtener_producto_evento_por_id(producto_id: int):
    try:
        with get_db_connection() as conn:
            producto = conn.execute("SELECT * FROM productos_eventos_empresa WHERE id_producto_evento = ?", (producto_id,)).fetchone()
            return dict(producto) if producto else None
    except Exception as e:
        logger.error(f"Error en obtener_producto_evento_por_id: {e}")
        return None

def borrar_producto_evento(producto_id: int, audit_user_id: int | None = None):
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM productos_eventos_empresa WHERE id_producto_evento = ?", (producto_id,))
            log_audit(audit_user_id, "DELETE_PRODUCTO_EVENTO", f"ID: {producto_id}")
            return True
    except Exception as e:
        logger.error(f"Error en borrar_producto_evento: {e}")
        return False

# --- Gestión de Registros de Clientes por Empresa ---
def registrar_cliente(datos: dict):
    # Esta función no usa el genérico porque es un INSERT simple sin update.
    sql = """
        INSERT INTO registros_clientes (empresa_id, pais_origen_cliente, fecha_registro, cantidad, audit_user_id)
        VALUES (:empresa_id, :pais_origen_cliente, :fecha_registro, :cantidad, :audit_user_id)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, datos)
            log_audit(datos.get('audit_user_id'), "CREATE_REGISTRO_CLIENTE", f"Empresa ID: {datos.get('empresa_id')}, Pais: {datos.get('pais_origen_cliente')}")
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error en registrar_cliente: {e}")
        return None

def obtener_resumen_clientes_por_empresa(empresa_id: int):
    """Retorna un conteo de clientes por país para una empresa específica."""
    query = """
        SELECT pais_origen_cliente, SUM(cantidad) as total_clientes
        FROM registros_clientes
        WHERE empresa_id = ?
        GROUP BY pais_origen_cliente
        ORDER BY total_clientes DESC
    """
    try:
        with get_db_connection() as conn:
            resultados = conn.execute(query, (empresa_id,)).fetchall()
            return [dict(row) for row in resultados]
    except Exception as e:
        logger.error(f"Error en obtener_resumen_clientes_por_empresa: {e}")
        return []

# ... y así para el resto de funciones ...
def listar_atractivos_admin_paginado(f, o, l, off): return [], 0
def crear_o_actualizar_atractivo(d, id=None): return 1

def obtener_atractivo_por_id(atractivo_id: int):
    try:
        with get_db_connection() as conn:
            atractivo = conn.execute("SELECT * FROM atractivos_turisticos WHERE id_atractivo = ?", (atractivo_id,)).fetchone()
            return dict(atractivo) if atractivo else None
    except Exception as e:
        logger.error(f"Error en obtener_atractivo_por_id: {e}")
        return None

def listar_vacantes_admin_paginado(f, o, l, off): return [], 0
def crear_o_actualizar_vacante(d, id=None): return 1

# --- Gestión de Restaurantes (RAT) ---
def listar_mesas_por_empresa(empresa_id: int):
    try:
        with get_db_connection() as conn:
            mesas = conn.execute("SELECT * FROM restaurante_mesas WHERE id_empresa = ?", (empresa_id,)).fetchall()
            return [dict(row) for row in mesas]
    except Exception as e:
        logger.error(f"Error en listar_mesas_por_empresa: {e}")
        return []

def crear_o_actualizar_mesa(datos: dict, mesa_id: int | None = None):
    return _crear_o_actualizar_generico("restaurante_mesas", "id_mesa", datos, mesa_id)

def listar_menu_por_empresa(empresa_id: int):
    try:
        with get_db_connection() as conn:
            menu = conn.execute("SELECT * FROM restaurante_menu_productos WHERE id_empresa = ?", (empresa_id,)).fetchall()
            return [dict(row) for row in menu]
    except Exception as e:
        logger.error(f"Error en listar_menu_por_empresa: {e}")
        return []

def crear_o_actualizar_producto_menu(datos: dict, producto_id: int | None = None):
    return _crear_o_actualizar_generico("restaurante_menu_productos", "id_producto", datos, producto_id)

def crear_pedido(datos: dict):
    return _crear_o_actualizar_generico("restaurante_pedidos", "id_pedido", datos, None)

def agregar_item_pedido(datos: dict):
    return _crear_o_actualizar_generico("restaurante_pedidos_items", "id_pedido_item", datos, None)

def listar_pedidos_abiertos_por_empresa(empresa_id: int):
    query = """
        SELECT p.*, m.nombre_mesa
        FROM restaurante_pedidos p
        JOIN restaurante_mesas m ON p.id_mesa = m.id_mesa
        WHERE m.id_empresa = ? AND p.estado != 'Cerrado'
    """
    try:
        with get_db_connection() as conn:
            pedidos = conn.execute(query, (empresa_id,)).fetchall()
            return [dict(row) for row in pedidos]
    except Exception as e:
        logger.error(f"Error en listar_pedidos_abiertos_por_empresa: {e}")
        return []

def listar_items_por_pedido(pedido_id: int):
    query = """
        SELECT i.*, p.nombre_producto
        FROM restaurante_pedidos_items i
        JOIN restaurante_menu_productos p ON i.id_producto = p.id_producto
        WHERE i.id_pedido = ?
    """
    try:
        with get_db_connection() as conn:
            items = conn.execute(query, (pedido_id,)).fetchall()
            return [dict(row) for row in items]
    except Exception as e:
        logger.error(f"Error en listar_items_por_pedido: {e}")
        return []

# --- Gestión de Agencias de Viajes (RAT) ---
def listar_paquetes_por_agencia(empresa_id: int):
    try:
        with get_db_connection() as conn:
            paquetes = conn.execute("SELECT * FROM agencia_paquetes WHERE id_empresa = ?", (empresa_id,)).fetchall()
            return [dict(row) for row in paquetes]
    except Exception as e:
        logger.error(f"Error en listar_paquetes_por_agencia: {e}")
        return []

def crear_o_actualizar_paquete(datos: dict, paquete_id: int | None = None):
    return _crear_o_actualizar_generico("agencia_paquetes", "id_paquete", datos, paquete_id)

def listar_reservas_paquetes_por_agencia(empresa_id: int):
    query = """
        SELECT r.*, p.nombre_paquete, u.nombre_completo as nombre_cliente
        FROM agencia_reservas_paquetes r
        JOIN agencia_paquetes p ON r.id_paquete = p.id_paquete
        JOIN usuarios u ON r.id_cliente = u.id_usuario
        WHERE p.id_empresa = ?
    """
    try:
        with get_db_connection() as conn:
            reservas = conn.execute(query, (empresa_id,)).fetchall()
            return [dict(row) for row in reservas]
    except Exception as e:
        logger.error(f"Error en listar_reservas_paquetes_por_agencia: {e}")
        return []

def crear_o_actualizar_reserva_paquete(datos: dict, reserva_id: int | None = None):
    return _crear_o_actualizar_generico("agencia_reservas_paquetes", "id_reserva_paquete", datos, reserva_id)

# --- Gestión de Guías Turísticos (RAT) ---
def crear_o_actualizar_perfil_guia(datos: dict, guia_id: int):
    # El id del perfil es el mismo que el del usuario
    datos["id_guia"] = guia_id
    return _crear_o_actualizar_generico("guias_perfiles", "id_guia", datos, guia_id)

def obtener_perfil_guia(guia_id: int):
    try:
        with get_db_connection() as conn:
            perfil = conn.execute("SELECT * FROM guias_perfiles WHERE id_guia = ?", (guia_id,)).fetchone()
            return dict(perfil) if perfil else None
    except Exception as e:
        logger.error(f"Error en obtener_perfil_guia: {e}")
        return None

def listar_guias_publico(filtros: dict):
    query = """
        SELECT u.id_usuario, u.nombre_completo, p.idiomas, p.especialidades, p.tarifa_por_hora
        FROM usuarios u
        JOIN guias_perfiles p ON u.id_usuario = p.id_guia
        WHERE u.rol_id = (SELECT id_rol FROM roles WHERE nombre_rol = 'GuiaTuristico')
    """
    # Aquí se podrían añadir más filtros
    try:
        with get_db_connection() as conn:
            guias = conn.execute(query).fetchall()
            return [dict(row) for row in guias]
    except Exception as e:
        logger.error(f"Error en listar_guias_publico: {e}")
        return []

def crear_reserva_tour(datos: dict):
    return _crear_o_actualizar_generico("guias_reservas_tours", "id_reserva_tour", datos, None)

def listar_reservas_tours_por_guia(guia_id: int):
    query = """
        SELECT r.*, u.nombre_completo as nombre_cliente
        FROM guias_reservas_tours r
        JOIN usuarios u ON r.id_cliente = u.id_usuario
        WHERE r.id_guia = ?
    """
    try:
        with get_db_connection() as conn:
            reservas = conn.execute(query, (guia_id,)).fetchall()
            return [dict(row) for row in reservas]
    except Exception as e:
        logger.error(f"Error en listar_reservas_tours_por_guia: {e}")
        return []

# --- Gestión de Inventario de Dotación ---
def crear_o_actualizar_tipo_item(datos: dict, tipo_item_id: int | None = None):
    return _crear_o_actualizar_generico("inventario_tipos_item", "id_tipo_item", datos, tipo_item_id)

def listar_tipos_item_por_empresa(empresa_id: int):
    try:
        with get_db_connection() as conn:
            tipos = conn.execute("SELECT * FROM inventario_tipos_item WHERE id_empresa = ?", (empresa_id,)).fetchall()
            return [dict(row) for row in tipos]
    except Exception as e:
        logger.error(f"Error en listar_tipos_item_por_empresa: {e}")
        return []

def registrar_item_individual(datos: dict):
    return _crear_o_actualizar_generico("inventario_items_individuales", "id_item_individual", datos, None)

def listar_items_individuales_por_tipo(tipo_item_id: int):
    try:
        with get_db_connection() as conn:
            items = conn.execute("SELECT * FROM inventario_items_individuales WHERE id_tipo_item = ?", (tipo_item_id,)).fetchall()
            return [dict(row) for row in items]
    except Exception as e:
        logger.error(f"Error en listar_items_individuales_por_tipo: {e}")
        return []

# --- Gestión de Precios Dinámicos ---
def crear_o_actualizar_regla_precio(datos: dict, regla_id: int | None = None):
    return _crear_o_actualizar_generico("reglas_precios", "id_regla", datos, regla_id)

def listar_reglas_precios_por_empresa(empresa_id: int):
    try:
        with get_db_connection() as conn:
            reglas = conn.execute("SELECT * FROM reglas_precios WHERE id_empresa = ?", (empresa_id,)).fetchall()
            return [dict(row) for row in reglas]
    except Exception as e:
        logger.error(f"Error en listar_reglas_precios_por_empresa: {e}")
        return []

def calcular_precio_final(recurso_id: int, fecha_inicio: str, fecha_fin: str):
    recurso = obtener_recurso_por_id(recurso_id)
    if not recurso:
        return 0

    precio_final = recurso.get("precio_base", 0)
    reglas = listar_reglas_precios_por_empresa(recurso["id_empresa"])

    # Lógica de aplicación de reglas (simplificada)
    for regla in reglas:
        if regla["tipo_regla"] == "temporada":
            if regla["fecha_inicio"] <= fecha_inicio and regla["fecha_fin"] >= fecha_fin:
                precio_final *= regla["valor_ajuste"]
        elif regla["tipo_regla"] == "dia_semana":
            # Lógica para aplicar reglas de días de la semana
            pass

    return precio_final

def obtener_recurso_por_id(recurso_id: int):
    try:
        with get_db_connection() as conn:
            recurso = conn.execute("SELECT * FROM recursos_reservables WHERE id_recurso = ?", (recurso_id,)).fetchone()
            return dict(recurso) if recurso else None
    except Exception as e:
        logger.error(f"Error en obtener_recurso_por_id: {e}")
        return None

# --- Gestión de Costos ---
def crear_o_actualizar_costo(datos: dict, costo_id: int | None = None):
    return _crear_o_actualizar_generico("costos_operativos", "id_costo", datos, costo_id)

def listar_costos_por_empresa(empresa_id: int):
    try:
        with get_db_connection() as conn:
            costos = conn.execute("SELECT * FROM costos_operativos WHERE id_empresa = ?", (empresa_id,)).fetchall()
            return [dict(row) for row in costos]
    except Exception as e:
        logger.error(f"Error en listar_costos_por_empresa: {e}")
        return []

# --- Gestión de Recursos Reservables ---
def crear_o_actualizar_recurso(datos: dict, recurso_id: int | None = None):
    return _crear_o_actualizar_generico("recursos_reservables", "id_recurso", datos, recurso_id)

def listar_recursos_por_empresa(empresa_id: int):
    try:
        with get_db_connection() as conn:
            recursos = conn.execute("SELECT * FROM recursos_reservables WHERE id_empresa = ?", (empresa_id,)).fetchall()
            return [dict(row) for row in recursos]
    except Exception as e:
        logger.error(f"Error en listar_recursos_por_empresa: {e}")
        return []

def listar_recursos_por_tipo_y_ciudad(tipo: str, ciudad: str, capacidad: int):
    query = """
        SELECT r.*
        FROM recursos_reservables r
        JOIN empresas_prestadores_turisticos e ON r.id_empresa = e.id_empresa
        JOIN municipios m ON e.codigo_municipio = m.codigo_municipio
        WHERE r.tipo_recurso = ? AND m.nombre_municipio LIKE ? AND r.capacidad >= ?
    """
    try:
        with get_db_connection() as conn:
            recursos = conn.execute(query, (tipo, f"%{ciudad}%", capacidad)).fetchall()
            return [dict(row) for row in recursos]
    except Exception as e:
        logger.error(f"Error en listar_recursos_por_tipo_y_ciudad: {e}")
        return []

def crear_o_actualizar_reserva(datos: dict, reserva_id: int | None = None):
    return _crear_o_actualizar_generico("reservas", "id_reserva", datos, reserva_id)

# ... etc ...
