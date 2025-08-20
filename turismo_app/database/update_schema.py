import sqlite3
import os

DB_NAME = "turismo_data_final.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def update_schema():
    """
    Aplica todas las actualizaciones de esquema necesarias a la base de datos.
    Es idempotente; se puede ejecutar de forma segura varias veces.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if conn is None:
        print("Error! No se pudo crear la conexión a la base de datos.")
        return

    print("Conexión exitosa. Verificando y actualizando esquema...")

    try:
        # --- MIGRACIÓN 1: Reconstruir restaurante_pedidos ---
        cursor.execute("PRAGMA table_info(restaurante_pedidos);")
        column_names = [info[1] for info in cursor.fetchall()]

        if 'tipo_orden' not in column_names:
            print("Iniciando migración de la tabla 'restaurante_pedidos'...")
            cursor.execute("BEGIN")
            try:
                cursor.execute("ALTER TABLE restaurante_pedidos RENAME TO restaurante_pedidos_old;")

                sql_create_new_pedidos_table = """
                CREATE TABLE restaurante_pedidos (
                    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT, id_mesa INTEGER, id_mesero INTEGER NOT NULL,
                    estado TEXT NOT NULL, total REAL, fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_cierre TIMESTAMP, tipo_orden TEXT NOT NULL DEFAULT 'Mesa',
                    cliente_nombre TEXT, cliente_direccion TEXT, cliente_telefono TEXT, id_empresa INTEGER,
                    FOREIGN KEY (id_mesa) REFERENCES restaurante_mesas (id_mesa),
                    FOREIGN KEY (id_mesero) REFERENCES usuarios (id_usuario),
                    FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
                );"""
                create_table(conn, sql_create_new_pedidos_table)

                sql_copy_data = """
                INSERT INTO restaurante_pedidos (id_pedido, id_mesa, id_mesero, estado, total, fecha_apertura, fecha_cierre)
                SELECT id_pedido, id_mesa, id_mesero, estado, total, fecha_apertura, fecha_cierre
                FROM restaurante_pedidos_old;
                """
                cursor.execute(sql_copy_data)
                cursor.execute("DROP TABLE restaurante_pedidos_old;")
                conn.commit()
                print("Tabla 'restaurante_pedidos' reconstruida exitosamente.")
            except sqlite3.OperationalError as e:
                print(f"No se pudo renombrar 'restaurante_pedidos', puede que ya se haya migrado. Error: {e}")
                conn.rollback()

        # --- MIGRACIÓN 2: Crear tablas adicionales si no existen ---
        cursor.execute("BEGIN")
        create_table(conn, """
        CREATE TABLE IF NOT EXISTS historial_estados_pedido (
            id_historial INTEGER PRIMARY KEY AUTOINCREMENT, id_pedido INTEGER NOT NULL, estado TEXT NOT NULL,
            fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP, notas TEXT, registrado_por_usuario_id INTEGER,
            FOREIGN KEY (id_pedido) REFERENCES restaurante_pedidos (id_pedido) ON DELETE CASCADE,
            FOREIGN KEY (registrado_por_usuario_id) REFERENCES usuarios (id_usuario)
        );""")
        create_table(conn, """
        CREATE TABLE IF NOT EXISTS inscripciones (
            id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT, id_evento INTEGER NOT NULL, id_usuario INTEGER NOT NULL,
            fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, estado TEXT NOT NULL DEFAULT 'Confirmada',
            FOREIGN KEY (id_evento) REFERENCES productos_eventos_empresa (id_producto_evento),
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        );""")
        create_table(conn, """
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );""")
        conn.commit()
        print("Tablas adicionales verificadas/creadas.")

        # --- MIGRACIÓN 3: Añadir columnas si no existen ---
        cursor.execute("BEGIN")
        cursor.execute("PRAGMA table_info(restaurante_menu_productos);")
        if 'id_categoria' not in [info[1] for info in cursor.fetchall()]:
            cursor.execute("ALTER TABLE restaurante_menu_productos ADD COLUMN id_categoria INTEGER REFERENCES categorias(id_categoria);")

        cursor.execute("PRAGMA table_info(productos_eventos_empresa);")
        if 'cupos_disponibles' not in [info[1] for info in cursor.fetchall()]:
            cursor.execute("ALTER TABLE productos_eventos_empresa ADD COLUMN cupos_disponibles INTEGER DEFAULT 0;")

        conn.commit()
        print("Verificación de columnas adicionales completa.")

    except Exception as e:
        print(f"Ocurrió un error durante la actualización del esquema: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Proceso de actualización de esquema finalizado.")

if __name__ == '__main__':
    update_schema()
