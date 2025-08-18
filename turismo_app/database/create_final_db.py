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
            id_empresa_asociada INTEGER,
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rol_id) REFERENCES roles (id_rol),
            FOREIGN KEY (codigo_municipio) REFERENCES municipios (codigo_municipio),
            FOREIGN KEY (codigo_departamento) REFERENCES departamentos (codigo_departamento),
            FOREIGN KEY (id_empresa_asociada) REFERENCES empresas_prestadores_turisticos (id_empresa)
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

        # --- Tablas Genéricas para el Motor de Reservas ---
        sql_create_recursos_reservables_table = """
        CREATE TABLE IF NOT EXISTS recursos_reservables (
            id_recurso INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            nombre_recurso TEXT NOT NULL,
            tipo_recurso TEXT NOT NULL,
            capacidad INTEGER NOT NULL,
            descripcion TEXT,
            precio_base REAL NOT NULL,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
        );"""

        sql_create_reservas_table = """
        CREATE TABLE IF NOT EXISTS reservas (
            id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
            id_recurso INTEGER NOT NULL,
            id_cliente INTEGER NOT NULL,
            fecha_inicio DATETIME NOT NULL,
            fecha_fin DATETIME NOT NULL,
            estado TEXT NOT NULL,
            monto_final REAL,
            id_promocion INTEGER,
            FOREIGN KEY (id_recurso) REFERENCES recursos_reservables (id_recurso),
            FOREIGN KEY (id_cliente) REFERENCES usuarios (id_usuario)
        );"""

        sql_create_promociones_table = """
        CREATE TABLE IF NOT EXISTS promociones (
            id_promocion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            codigo_promocion TEXT UNIQUE,
            descripcion TEXT,
            tipo_descuento TEXT, -- "porcentaje" o "fijo"
            valor_descuento REAL,
            fecha_inicio DATE,
            fecha_fin DATE,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
        );"""

        sql_create_pagos_table = """
        CREATE TABLE IF NOT EXISTS pagos (
            id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
            id_reserva INTEGER NOT NULL,
            monto REAL NOT NULL,
            metodo_pago TEXT,
            estado_pago TEXT,
            fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_reserva) REFERENCES reservas (id_reserva)
        );"""

        sql_create_reglas_precios_table = """
        CREATE TABLE IF NOT EXISTS reglas_precios (
            id_regla INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            nombre_regla TEXT NOT NULL,
            tipo_regla TEXT NOT NULL, -- "temporada", "dia_semana", "demanda"
            valor_ajuste REAL NOT NULL, -- Puede ser un porcentaje (ej. 1.2 para +20%) o un monto fijo
            fecha_inicio DATE,
            fecha_fin DATE,
            dias_semana TEXT, -- "1,2,3,4,5" para L-V
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
        );"""

        # --- Tablas para el Módulo de Restaurantes (RAT) ---
        sql_create_restaurante_mesas_table = """
        CREATE TABLE IF NOT EXISTS restaurante_mesas (
            id_mesa INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            nombre_mesa TEXT NOT NULL, -- Ej: "Mesa 5", "Barra 1"
            capacidad INTEGER NOT NULL,
            estado TEXT NOT NULL, -- "Libre", "Ocupada", "Reservada"
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
        );"""

        sql_create_restaurante_menu_productos_table = """
        CREATE TABLE IF NOT EXISTS restaurante_menu_productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            nombre_producto TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            categoria TEXT, -- "Entradas", "Platos Fuertes", "Bebidas"
            disponible INTEGER DEFAULT 1,
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
        );"""

        sql_create_restaurante_pedidos_table = """
        CREATE TABLE IF NOT EXISTS restaurante_pedidos (
            id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
            id_mesa INTEGER NOT NULL,
            id_mesero INTEGER NOT NULL,
            estado TEXT NOT NULL, -- "Abierto", "Enviado a Cocina", "Cerrado"
            total REAL,
            fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_cierre TIMESTAMP,
            FOREIGN KEY (id_mesa) REFERENCES restaurante_mesas (id_mesa),
            FOREIGN KEY (id_mesero) REFERENCES usuarios (id_usuario)
        );"""

        sql_create_restaurante_pedidos_items_table = """
        CREATE TABLE IF NOT EXISTS restaurante_pedidos_items (
            id_pedido_item INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pedido INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            estado TEXT NOT NULL, -- "Pedido", "En Preparación", "Entregado"
            notas TEXT,
            FOREIGN KEY (id_pedido) REFERENCES restaurante_pedidos (id_pedido),
            FOREIGN KEY (id_producto) REFERENCES restaurante_menu_productos (id_producto)
        );"""

        # --- Tablas para el Módulo de Agencias de Viajes (RAT) ---
        sql_create_agencia_paquetes_table = """
        CREATE TABLE IF NOT EXISTS agencia_paquetes (
            id_paquete INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            nombre_paquete TEXT NOT NULL,
            descripcion TEXT,
            precio_total REAL NOT NULL,
            duracion_dias INTEGER,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
        );"""

        sql_create_paquete_servicios_table = """
        CREATE TABLE IF NOT EXISTS paquete_servicios (
            id_paquete_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paquete INTEGER NOT NULL,
            tipo_servicio TEXT NOT NULL, -- "hotel", "tour", "transporte"
            id_servicio_especifico INTEGER NOT NULL,
            descripcion_servicio TEXT,
            FOREIGN KEY (id_paquete) REFERENCES agencia_paquetes (id_paquete)
        );"""

        sql_create_agencia_reservas_paquetes_table = """
        CREATE TABLE IF NOT EXISTS agencia_reservas_paquetes (
            id_reserva_paquete INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paquete INTEGER NOT NULL,
            id_cliente INTEGER NOT NULL, -- Podría ser un id de la tabla usuarios o una nueva tabla de clientes
            fecha_inicio DATE NOT NULL,
            numero_personas INTEGER NOT NULL,
            estado TEXT NOT NULL, -- "Confirmada", "Cancelada", "Completada"
            FOREIGN KEY (id_paquete) REFERENCES agencia_paquetes (id_paquete)
        );"""

        # --- Tablas para el Módulo de Guías Turísticos (RAT) ---
        sql_create_guias_perfiles_table = """
        CREATE TABLE IF NOT EXISTS guias_perfiles (
            id_guia INTEGER PRIMARY KEY, -- Coincide con id_usuario
            idiomas TEXT, -- "Español,Inglés"
            especialidades TEXT, -- "Historia,Naturaleza"
            certificaciones TEXT,
            tarifa_por_hora REAL,
            FOREIGN KEY (id_guia) REFERENCES usuarios (id_usuario)
        );"""

        sql_create_guias_disponibilidad_table = """
        CREATE TABLE IF NOT EXISTS guias_disponibilidad (
            id_disponibilidad INTEGER PRIMARY KEY AUTOINCREMENT,
            id_guia INTEGER NOT NULL,
            fecha DATE NOT NULL,
            disponible INTEGER NOT NULL, -- 0 para no disponible, 1 para disponible
            FOREIGN KEY (id_guia) REFERENCES usuarios (id_usuario)
        );"""

        sql_create_guias_reservas_tours_table = """
        CREATE TABLE IF NOT EXISTS guias_reservas_tours (
            id_reserva_tour INTEGER PRIMARY KEY AUTOINCREMENT,
            id_guia INTEGER NOT NULL,
            id_cliente INTEGER NOT NULL,
            fecha_hora_inicio DATETIME NOT NULL,
            duracion_horas INTEGER NOT NULL,
            estado TEXT NOT NULL, -- "Solicitada", "Confirmada", "Cancelada"
            FOREIGN KEY (id_guia) REFERENCES usuarios (id_usuario),
            FOREIGN KEY (id_cliente) REFERENCES usuarios (id_usuario)
        );"""

        # --- Tabla de Inventario de Dotación ---
        # --- Tablas de Inventario de Dotación ---
        sql_create_inventario_tipos_item_table = """
        CREATE TABLE IF NOT EXISTS inventario_tipos_item (
            id_tipo_item INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            nombre_tipo TEXT NOT NULL,
            categoria TEXT,
            descripcion TEXT,
            stock_minimo_deseado INTEGER,
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
        );"""

        sql_create_inventario_items_individuales_table = """
        CREATE TABLE IF NOT EXISTS inventario_items_individuales (
            id_item_individual INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tipo_item INTEGER NOT NULL,
            estado TEXT NOT NULL,
            fecha_compra DATE,
            veces_usado INTEGER DEFAULT 0,
            fecha_ultimo_mantenimiento DATE,
            notas_mantenimiento TEXT,
            FOREIGN KEY (id_tipo_item) REFERENCES inventario_tipos_item (id_tipo_item)
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
        create_table(conn, sql_create_recursos_reservables_table)
        create_table(conn, sql_create_reservas_table)
        create_table(conn, sql_create_promociones_table)
        create_table(conn, sql_create_pagos_table)
        create_table(conn, sql_create_reglas_precios_table)
        create_table(conn, sql_create_restaurante_mesas_table)
        create_table(conn, sql_create_restaurante_menu_productos_table)
        create_table(conn, sql_create_restaurante_pedidos_table)
        create_table(conn, sql_create_restaurante_pedidos_items_table)
        create_table(conn, sql_create_agencia_paquetes_table)
        create_table(conn, sql_create_paquete_servicios_table)
        create_table(conn, sql_create_agencia_reservas_paquetes_table)
        create_table(conn, sql_create_guias_perfiles_table)
        create_table(conn, sql_create_guias_disponibilidad_table)
        create_table(conn, sql_create_guias_reservas_tours_table)
        create_table(conn, sql_create_inventario_tipos_item_table)
        create_table(conn, sql_create_inventario_items_individuales_table)
        print("Tablas creadas.")

        # --- Insertar Datos Iniciales ---
        print("Insertando datos iniciales...")
        c = conn.cursor()

        sql_create_productos_eventos_table = """
        CREATE TABLE IF NOT EXISTS productos_eventos_empresa (
            id_producto_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            tipo TEXT NOT NULL, -- 'Producto' o 'Evento'
            precio REAL,
            fecha_evento DATE,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
        );"""

        sql_create_registros_clientes_table = """
        CREATE TABLE IF NOT EXISTS registros_clientes (
            id_registro_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empresa INTEGER NOT NULL,
            nacionalidad TEXT NOT NULL, -- 'Nacional' o 'Extranjero'
            cantidad INTEGER DEFAULT 1,
            fecha_registro DATE NOT NULL,
            FOREIGN KEY (id_empresa) REFERENCES empresas_prestadores_turisticos (id_empresa)
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
        create_table(conn, sql_create_productos_eventos_table)
        create_table(conn, sql_create_registros_clientes_table)
        print("Tablas creadas.")

        # --- Insertar Datos Iniciales ---
        print("Insertando datos iniciales...")
        c = conn.cursor()

        # Roles
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('SuperAdmin', 'Control total del sistema'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('AdminMunicipal', 'Gestor de contenido de un municipio'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('PropietarioEmpresa', 'Dueño de un negocio turístico'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('Ciudadano', 'Usuario público de la aplicación'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('ChefEjecutivo', 'Jefe de cocina'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('JefeDeSala', 'Maître o jefe de sala'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('Camarero', 'Mesero o camarero'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('Hostess', 'Recepcionista de restaurante'))
        c.execute("INSERT INTO roles (nombre_rol, descripcion) VALUES (?, ?)", ('GuiaTuristico', 'Guía turístico profesional'))

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
