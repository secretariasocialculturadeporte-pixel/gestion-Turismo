import sqlite3
import os

DB_NAME = "turismo_data_final.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

def get_db_connection():
    """Crea una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def create_table(conn, create_table_sql):
    """Crea una tabla a partir de la declaración SQL proporcionada."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def update_schema():
    """Añade las nuevas tablas y modifica las existentes para el gestor de comandas."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if conn is not None:
        print("Conexión exitosa. Actualizando esquema para el gestor de comandas...")

        try:
            # Iniciar transacción
            cursor.execute("BEGIN")

            # 1. Reconstruir la tabla restaurante_pedidos para hacer id_mesa nullable y añadir nuevos campos
            print("Reconstruyendo la tabla 'restaurante_pedidos'...")

            # Renombrar la tabla vieja si existe
            cursor.execute("ALTER TABLE restaurante_pedidos RENAME TO restaurante_pedidos_old;")

            # Crear la nueva tabla con la estructura deseada
            sql_create_new_pedidos_table = """
            CREATE TABLE restaurante_pedidos (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                id_mesa INTEGER,
                id_mesero INTEGER NOT NULL,
                estado TEXT NOT NULL,
                total REAL,
                fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_cierre TIMESTAMP,
                tipo_orden TEXT NOT NULL DEFAULT 'Mesa',
                cliente_nombre TEXT,
                cliente_direccion TEXT,
                cliente_telefono TEXT,
                FOREIGN KEY (id_mesa) REFERENCES restaurante_mesas (id_mesa),
                FOREIGN KEY (id_mesero) REFERENCES usuarios (id_usuario)
            );"""
            create_table(conn, sql_create_new_pedidos_table)

            # Copiar los datos de la tabla vieja a la nueva
            # Se asume que todos los pedidos existentes son de tipo 'Mesa'
            sql_copy_data = """
            INSERT INTO restaurante_pedidos (id_pedido, id_mesa, id_mesero, estado, total, fecha_apertura, fecha_cierre)
            SELECT id_pedido, id_mesa, id_mesero, estado, total, fecha_apertura, fecha_cierre
            FROM restaurante_pedidos_old;
            """
            cursor.execute(sql_copy_data)

            # Borrar la tabla vieja
            cursor.execute("DROP TABLE restaurante_pedidos_old;")
            print("Tabla 'restaurante_pedidos' reconstruida exitosamente.")

            # 2. Crear la tabla para el historial de estados de pedidos
            sql_create_historial_table = """
            CREATE TABLE IF NOT EXISTS historial_estados_pedido (
                id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER NOT NULL,
                estado TEXT NOT NULL,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notas TEXT,
                registrado_por_usuario_id INTEGER,
                FOREIGN KEY (id_pedido) REFERENCES restaurante_pedidos (id_pedido) ON DELETE CASCADE,
                FOREIGN KEY (registrado_por_usuario_id) REFERENCES usuarios (id_usuario)
            );"""
            create_table(conn, sql_create_historial_table)
            print("Tabla 'historial_estados_pedido' creada o ya existente.")

            # 3. Añadir columna de categoría a la tabla de productos de menú
            try:
                cursor.execute("ALTER TABLE restaurante_menu_productos ADD COLUMN id_categoria INTEGER REFERENCES categorias(id_categoria);")
                print("Columna 'id_categoria' añadida a 'restaurante_menu_productos'.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("La columna 'id_categoria' ya existe en 'restaurante_menu_productos'.")
                else:
                    raise e

            # 4. Añadir columna de empresa a la tabla de pedidos
            try:
                cursor.execute("ALTER TABLE restaurante_pedidos ADD COLUMN id_empresa INTEGER REFERENCES empresas_prestadores_turisticos(id_empresa);")
                print("Columna 'id_empresa' añadida a 'restaurante_pedidos'.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("La columna 'id_empresa' ya existe en 'restaurante_pedidos'.")
                else:
                    raise e

            # Commit de la transacción
            conn.commit()
            print("Esquema actualizado y conexión cerrada.")

        except sqlite3.OperationalError as e:
            # Esto puede pasar si el script ya se ejecutó.
            # Si la tabla _old no existe, es probable que ya se haya migrado.
            if "no such table: restaurante_pedidos_old" in str(e) or "no such table: restaurante_pedidos" in str(e):
                 print("Parece que el esquema ya fue actualizado anteriormente. No se realizarán cambios.")
                 conn.rollback()
            else:
                print(f"Error operacional durante la actualización del esquema: {e}")
                conn.rollback()
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            conn.rollback()
        finally:
            conn.close()
    else:
        print("Error! No se pudo crear la conexión a la base de datos.")

if __name__ == '__main__':
    print("Iniciando actualización del esquema de la base de datos...")
    update_schema()
    print("Actualización del esquema finalizada.")
