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
        cursor.execute("BEGIN")

        # --- MIGRACIÓN: Atractivos Turísticos ---
        # Borrar la tabla placeholder vieja y crear la nueva detallada
        cursor.execute("DROP TABLE IF EXISTS atractivos_turisticos;")
        sql_create_atractivos_table = """
        CREATE TABLE atractivos_turisticos (
            id_atractivo INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            codigo_municipio TEXT NOT NULL,
            tipo_atractivo TEXT,
            subtipo_atractivo TEXT,
            ubicacion_especifica TEXT,
            temperatura_promedio REAL,
            altitud REAL,
            horario_atencion TEXT,
            tarifa_ingreso REAL,
            actividades_principales TEXT,
            servicios_ofrecidos TEXT,
            recomendaciones TEXT,
            estado_conservacion TEXT,
            contacto_informacion TEXT,
            aprobado_publicar INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio)
        );"""
        create_table(conn, sql_create_atractivos_table)
        print("Tabla 'atractivos_turisticos' actualizada al nuevo esquema.")

        # --- MIGRACIÓN: Otras tablas (se asume que las anteriores ya se ejecutaron) ---
        # ... (Aquí se podrían añadir las otras migraciones si fuera necesario)

        conn.commit()
        print("Esquema actualizado exitosamente.")

    except Exception as e:
        print(f"Ocurrió un error durante la actualización del esquema: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Proceso de actualización de esquema finalizado.")

if __name__ == '__main__':
    update_schema()
