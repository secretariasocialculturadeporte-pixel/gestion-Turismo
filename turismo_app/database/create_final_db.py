import sqlite3
import os
import hashlib

DB_NAME = "turismo_data_final.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"Conexión a SQLite DB en '{DB_PATH}' exitosa (versión: {sqlite3.version})")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """Crea una tabla a partir de la declaración SQL proporcionada."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def setup_database():
    """Crea la base de datos y todas las tablas necesarias."""
    # Eliminar la base de datos anterior si existe para un inicio limpio
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Base de datos '{DB_NAME}' existente eliminada.")

    conn = create_connection()

    if conn is not None:
        # --- Tablas de Geografía ---
        sql_create_departamentos_table = """
        CREATE TABLE IF NOT EXISTS departamentos (
            codigo_departamento TEXT PRIMARY KEY,
            nombre_departamento TEXT NOT NULL
        );"""

        sql_create_municipios_table = """
        CREATE TABLE IF NOT EXISTS municipios (
            codigo_municipio TEXT PRIMARY KEY,
            nombre_municipio TEXT NOT NULL,
            codigo_departamento TEXT NOT NULL,
            FOREIGN KEY (codigo_departamento) REFERENCES departamentos (codigo_departamento)
        );"""

        # --- Tablas de Usuarios y Roles ---
        sql_create_roles_table = """
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT NOT NULL UNIQUE,
            descripcion TEXT
        );"""

        sql_create_usuarios_table = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL UNIQUE,
            nombre_completo TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            rol_id INTEGER NOT NULL,
            codigo_municipio TEXT,
            codigo_departamento TEXT,
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rol_id) REFERENCES roles (id_rol),
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio),
            FOREIGN KEY (codigo_departamento) REFERENCES departamentos (codigo_departamento)
        );"""

        # --- Tablas de Contenido Principal ---
        sql_create_empresas_table = """
        CREATE TABLE IF NOT EXISTS empresas_prestadores_turisticos (
            id_empresa INTEGER PRIMARY KEY AUTOINCREMENT,
            razon_social_o_nombre_comercial TEXT NOT NULL,
            nit TEXT UNIQUE,
            tipo_prestador TEXT NOT NULL,
            tipo_prestador_otro TEXT,
            es_formal INTEGER DEFAULT 1,
            rnt TEXT,
            descripcion_servicios TEXT,
            direccion_principal TEXT,
            telefonos_contacto TEXT,
            email_contacto TEXT,
            pagina_web TEXT,
            aprobada_publicar INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1,
            codigo_municipio TEXT NOT NULL,
            registrada_por_usuario_id INTEGER,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_ultima_actualizacion TIMESTAMP,
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio),
            FOREIGN KEY (registrada_por_usuario_id) REFERENCES usuarios (id_usuario)
        );"""

        sql_create_vacantes_table = """
        CREATE TABLE IF NOT EXISTS vacantes_empleo (
            id_vacante INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo_vacante TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            requisitos TEXT,
            empresa_id INTEGER,
            nombre_empleador_alternativo TEXT,
            tipo_contrato TEXT,
            salario_rango TEXT,
            fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_cierre TIMESTAMP,
            activa INTEGER DEFAULT 1,
            codigo_municipio TEXT NOT NULL,
            publicada_por_usuario_id INTEGER,
            FOREIGN KEY (empresa_id) REFERENCES empresas_prestadores_turisticos (id_empresa),
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio),
            FOREIGN KEY (publicada_por_usuario_id) REFERENCES usuarios (id_usuario)
        );"""

        # --- Tablas de Encuestas y Feedback ---
        sql_create_turistas_registros_table = """
        CREATE TABLE IF NOT EXISTS turistas_registros (
            id_turista_registro INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_encuesta DATE NOT NULL,
            nombre_turista TEXT,
            genero TEXT,
            edad INTEGER,
            rango_edad TEXT,
            nacionalidad TEXT,
            pais_residencia TEXT,
            codigo_depto_origen TEXT,
            codigo_municipio_origen TEXT,
            motivo_viaje TEXT,
            otro_motivo_viaje TEXT,
            codigo_municipio_encuestado TEXT NOT NULL,
            registrado_por_usuario_id INTEGER,
            FOREIGN KEY (codigo_municipio_encuestado) REFERENCES municipios (codigo_municipio),
            FOREIGN KEY (registrado_por_usuario_id) REFERENCES usuarios (id_usuario)
        );"""

        sql_create_encuestas_percepcion_table = """
        CREATE TABLE IF NOT EXISTS encuestas_percepcion (
            id_encuesta_percepcion INTEGER PRIMARY KEY AUTOINCREMENT,
            turista_registro_id INTEGER NOT NULL,
            -- CAMPOS DINAMICOS DE PERCEPCION (Ejemplo)
            volveria INTEGER,
            experiencia_general_positiva INTEGER,
            -- Agrega aquí más campos según tu definición de CAMPOS_PERCEPCION
            -- Se recomienda usar un esquema más flexible (ej. EAV) o generar las columnas dinámicamente
            -- pero para este ejemplo, se usarán columnas fijas.
            fecha_valoracion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (turista_registro_id) REFERENCES turistas_registros (id_turista_registro)
        );"""

        # --- Tablas Placeholder (a la espera de detalles del usuario) ---
        sql_create_atractivos_table = """
        /*
        PLACEHOLDER: Esta tabla debe ser actualizada con los campos detallados
        del Formato Único de Inventarios Turísticos del MinCIT.
        */
        CREATE TABLE IF NOT EXISTS atractivos_turisticos (
            id_atractivo INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_atractivo TEXT NOT NULL,
            tipo_categoria_principal TEXT,
            descripcion_breve TEXT,
            codigo_municipio TEXT NOT NULL,
            aprobado_publicar INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio)
        );"""

        sql_create_diagnostico_table = """
        /*
        PLACEHOLDER: Esta tabla debe ser actualizada con los campos detallados
        de la Metodología de Nivel de Desarrollo Turístico Territorial.
        */
        CREATE TABLE IF NOT EXISTS diagnostico_territorial (
            id_diagnostico INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_municipio TEXT NOT NULL UNIQUE,
            anio_diagnostico INTEGER NOT NULL,
            dimension_1_infraestructura REAL,
            dimension_2_sostenibilidad REAL,
            resultado_total REAL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            registrado_por_usuario_id INTEGER,
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio),
            FOREIGN KEY (registrado_por_usuario_id) REFERENCES usuarios (id_usuario)
        );"""

        sql_create_iniciativas_table = """
        CREATE TABLE IF NOT EXISTS iniciativas_turisticas (
            id_iniciativa INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_iniciativa TEXT NOT NULL,
            tipo_iniciativa TEXT, -- Plan, Programa, Proyecto
            descripcion TEXT,
            estado TEXT, -- Formulación, Ejecución, Terminado
            presupuesto REAL,
            codigo_municipio TEXT,
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio)
        );"""

        sql_create_eventos_table = """
        CREATE TABLE IF NOT EXISTS eventos_turisticos (
            id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_evento TEXT NOT NULL,
            fecha_inicio DATE,
            fecha_fin DATE,
            descripcion TEXT,
            publicado INTEGER DEFAULT 0,
            codigo_municipio TEXT,
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio)
        );"""

        # Crear todas las tablas
        print("Creando tablas...")
        create_table(conn, sql_create_departamentos_table)
        create_table(conn, sql_create_municipios_table)
        create_table(conn, sql_create_roles_table)
        create_table(conn, sql_create_usuarios_table)
        create_table(conn, sql_create_empresas_table)
        create_table(conn, sql_create_vacantes_table)
        create_table(conn, sql_create_turistas_registros_table)
        create_table(conn, sql_create_encuestas_percepcion_table)
        create_table(conn, sql_create_atractivos_table)
        create_table(conn, sql_create_diagnostico_table)
        create_table(conn, sql_create_iniciativas_table)
        create_table(conn, sql_create_eventos_table)
        print("Tablas creadas.")

        # --- Insertar Datos Iniciales ---
        print("Insertando datos iniciales...")
        c = conn.cursor()

        # Roles
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('SuperAdmin', 'Control total del sistema'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('AdminMunicipal', 'Gestor de contenido de un municipio'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('Ciudadano', 'Usuario público de la aplicación'))

        # Departamentos
        deptos = [('05', 'ANTIOQUIA'), ('08', 'ATLÁNTICO'), ('13', 'BOLÍVAR')]
        c.executemany("INSERT INTO departamentos (codigo_departamento, nombre_departamento) VALUES (?, ?)", deptos)

        # Municipios
        munis = [
            ('05001', 'MEDELLÍN', '05'), ('05360', 'JARDÍN', '05'),
            ('08001', 'BARRANQUILLA', '08'), ('08573', 'PUERTO COLOMBIA', '08'),
            ('13001', 'CARTAGENA', '13')
        ]
        c.executemany("INSERT INTO municipios (codigo_municipio, nombre_municipio, codigo_departamento) VALUES (?, ?, ?)", munis)

        # Usuario Admin de prueba
        admin_pass_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("""
            INSERT INTO usuarios (nombre_usuario, nombre_completo, email, password_hash, rol_id, activo)
            VALUES (?, ?, ?, ?, (SELECT id_rol FROM roles WHERE nombre_rol = 'SuperAdmin'), 1)
        """, ('admin', 'Administrador Principal', 'admin@turismo.com', admin_pass_hash))

        # Usuario Gestor de prueba
        gestor_pass_hash = hashlib.sha256('gestor123'.encode()).hexdigest()
        c.execute("""
            INSERT INTO usuarios (nombre_usuario, nombre_completo, email, password_hash, rol_id, codigo_municipio, codigo_departamento, activo)
            VALUES (?, ?, ?, ?, (SELECT id_rol FROM roles WHERE nombre_rol = 'AdminMunicipal'), '05001', '05', 1)
        """, ('gestor_med', 'Gestor Medellín', 'gestor.med@turismo.com', gestor_pass_hash))

        conn.commit()
        print("Datos iniciales insertados.")
        conn.close()
        print("Conexión a la base de datos cerrada.")

    else:
        print("Error! No se pudo crear la conexión a la base de datos.")

if __name__ == '__main__':
    print("Iniciando configuración de la base de datos...")
    setup_database()
    print("Configuración de la base de datos finalizada.")
