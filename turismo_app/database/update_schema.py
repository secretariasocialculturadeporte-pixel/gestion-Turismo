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
    """Añade las nuevas tablas de categorías a la base de datos existente."""
    conn = get_db_connection()

    if conn is not None:
        print("Conexión exitosa. Actualizando esquema...")

        # --- Tabla para Categorías Jerárquicas de Empresas ---
        sql_create_categorias_table = """
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_categoria TEXT NOT NULL,
            descripcion TEXT,
            id_categoria_padre INTEGER,
            FOREIGN KEY (id_categoria_padre) REFERENCES categorias (id_categoria)
        );"""

        # --- Tabla de Enlace (Muchos a Muchos) entre Empresas y Categorías ---
        sql_create_empresa_categorias_table = """
        CREATE TABLE IF NOT EXISTS empresa_categorias (
            id_empresa INTEGER NOT NULL,
            id_categoria INTEGER NOT NULL,
            PRIMARY KEY (id_empresa, id_categoria),
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa) ON DELETE CASCADE,
            FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria) ON DELETE CASCADE
        );"""

        # --- Índice para la tabla de categorías para búsquedas más rápidas ---
        sql_create_categorias_index = "CREATE INDEX IF NOT EXISTS idx_id_categoria_padre ON categorias (id_categoria_padre);"

        create_table(conn, sql_create_categorias_table)
        print("Tabla 'categorias' creada o ya existente.")

        create_table(conn, sql_create_empresa_categorias_table)
        print("Tabla 'empresa_categorias' creada o ya existente.")

        create_table(conn, sql_create_categorias_index)
        print("Índice en 'categorias' creado o ya existente.")

        conn.commit()
        conn.close()
        print("Esquema actualizado y conexión cerrada.")
    else:
        print("Error! No se pudo crear la conexión a la base de datos.")

if __name__ == '__main__':
    print("Iniciando actualización del esquema de la base de datos...")
    update_schema()
    print("Actualización del esquema finalizada.")
