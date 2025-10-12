# Informe Detallado del Proyecto: Sistema de Gestión Turística Territorial

## 1. Estado Actual y Arquitectura General

El proyecto es una aplicación de escritorio desarrollada en **Python** con el framework **Flet**. No sigue una arquitectura web tradicional (como Django/Flask con un frontend en HTML/JS), sino que Flet gestiona tanto la lógica como la interfaz de usuario en una única base de código.

- **Framework UI:** Flet (permite crear aplicaciones interactivas para escritorio, web y móvil).
- **Base de Datos:** SQLite, un sistema de base de datos local y basado en archivos (`turismo_data_final.db`).
- **Inteligencia Artificial:** Utiliza **LangChain** y **LangGraph** para orquestar un agente conversacional (chatbot) que se conecta a un modelo de lenguaje local (`llama3` a través de `ChatOllama`).

La aplicación está diseñada para ser un sistema centralizado que digitaliza y optimiza la gestión de servicios turísticos en un territorio (municipio o departamento).

## 2. Diagrama y Descripción de Carpetas

A continuación, se presenta un diagrama de la estructura de carpetas y una descripción de su propósito.

```
.
├── turismo_app/              # Directorio principal de la aplicación
│   ├── agents/               # Lógica del agente de IA (chatbot)
│   │   └── turismo_agent.py
│   ├── assets/               # Archivos estáticos (manifest.json, etc.)
│   ├── core/                 # Lógica de negocio principal y utilidades
│   │   ├── assets_manager.py
│   │   ├── audit_logger.py
│   │   └── mincit_definitions.py
│   ├── database/             # Módulos de acceso a la base de datos y el archivo .db
│   │   ├── create_final_db.py
│   │   └── db_manager.py
│   ├── logs/                 # Archivos de log (registros de auditoría)
│   │   └── audit.log
│   └── views/                # Lógica para construir las diferentes pantallas (vistas)
│       ├── admin/
│       ├── ciudadano/
│       ├── empresa/
│       ├── guia/
│       ├── shared/
│       ├── chatbot_view.py
│       ├── home_view.py
│       └── login_view.py
├── main.py                   # Punto de entrada de la aplicación, gestiona rutas y navegación
└── requirements.txt          # Dependencias del proyecto
```

### Descripción Detallada:

- **`turismo_app/`**: Contiene todo el código fuente de la aplicación.
  - **`agents/`**: Define el comportamiento del asistente de IA. `turismo_agent.py` integra LangChain, define las herramientas que el agente puede usar (como `buscar_recursos` o `crear_reserva`) y procesa las preguntas de los usuarios.
  - **`assets/`**: Almacena archivos estáticos necesarios para la aplicación, como el `manifest.json` para PWA (Progressive Web App).
  - **`core/`**: Módulos transversales.
    - `audit_logger.py`: Sistema para registrar acciones importantes (crear, modificar, borrar) en un log de auditoría (`audit.log`).
    - `mincit_definitions.py`: Probablemente contiene definiciones, constantes o datos relacionados con el Ministerio de Comercio, Industria y Turismo (MINCIT) de Colombia.
  - **`database/`**: Gestiona la interacción con la base de datos SQLite.
    - `db_manager.py`: Es el corazón del acceso a datos. Contiene funciones para obtener, insertar, actualizar y borrar registros en la base de datos (empresas, productos, usuarios, etc.).
    - `create_final_db.py`: Script para crear y poblar la base de datos inicial.
  - **`logs/`**: Guarda los registros generados por la aplicación, como el `audit.log`.
  - **`views/`**: La parte más extensa, define la interfaz de usuario para cada sección de la aplicación.
    - **Subcarpetas (`admin`, `ciudadano`, `empresa`, `guia`)**: Organizan las vistas según el rol del usuario. Por ejemplo, `admin/` contiene las pantallas que solo los administradores pueden ver.
    - **Archivos directos (`chatbot_view.py`, `home_view.py`, `login_view.py`)**: Vistas comunes o principales.
- **`main.py`**: Es el orquestador principal. Define todas las rutas de la aplicación (ej. `/login`, `/admin/dashboard`), maneja la navegación entre vistas, gestiona la sesión del usuario (autenticación) y monta la estructura principal de la UI (barra de navegación, menú superior).
- **`requirements.txt`**: Lista las librerías de Python necesarias para que el proyecto funcione (`flet`, `langchain`, etc.).

## 3. Funcionalidades de Cara al Cliente Final

El sistema ofrece un portal multifacético adaptado a las necesidades de diferentes actores del sector turístico.

### Para el Turista / Ciudadano:

1.  **Exploración Turística (`/ciudadano/turismo`)**:
    - **Consulta de Atractivos**: Puede ver una lista de atractivos turísticos (parques, museos, etc.) con descripciones, ubicaciones y fotos.
    - **Búsqueda de Empresas**: Puede buscar y filtrar proveedores de servicios turísticos (hoteles, restaurantes, agencias) por tipo y ubicación.
    - **Visualización de Productos y Eventos**: Puede ver los productos, eventos o paquetes que ofrecen las empresas.

2.  **Oportunidades de Empleo (`/ciudadano/empleo`)**:
    - Un portal donde las empresas turísticas publican vacantes, y los ciudadanos pueden buscarlas y aplicar.

3.  **Búsqueda y Contratación de Guías (`/ciudadano/guias`)**:
    - Permite buscar guías turísticos registrados, ver sus perfiles (especialidades, idiomas, tarifas) y probablemente contactarlos o reservar sus servicios.

4.  **Asistente Virtual (Chatbot) (`/chatbot`)**:
    - Un chatbot inteligente que responde preguntas en lenguaje natural.
    - Puede ayudar a:
      - "Encontrar un hotel en Salento para 2 personas".
      - "Reservar un tour de café para el próximo sábado".
      - "¿Qué paquetes turísticos hay disponibles en el Eje Cafetero?".

5.  **Sistema de Feedback (`/ciudadano/feedback`)**:
    - Un canal para que los usuarios dejen comentarios, sugerencias o quejas sobre los servicios o la plataforma en general.

### Para la Empresa / Prestador de Servicios Turísticos (Rol: `PropietarioEmpresa`):

1.  **Dashboard Principal (`/empresa/dashboard`)**:
    - Panel de control con estadísticas clave: resumen de reservas, clientes recientes, productos más vendidos, etc.

2.  **Gestión de Productos y Eventos (`/empresa/productos`)**:
    - Crear, editar y eliminar los servicios que ofrece la empresa (ej. tours, menús, habitaciones de hotel, paquetes turísticos).

3.  **Registro de Clientes (`/empresa/clientes`)**:
    - Un sistema para registrar manualmente la afluencia de clientes, especificando su país de origen. Esto es útil para generar estadísticas de turismo.

4.  **Gestión de Recursos y Disponibilidad (`/empresa/recursos`, `/empresa/calendario`)**:
    - Definir y gestionar los recursos físicos (habitaciones, vehículos, mesas) y su disponibilidad a lo largo del tiempo.

5.  **Módulos Específicos por Tipo de Empresa**:
    - **Restaurantes**: Gestión de menús, mesas, un sistema de Terminal Punto de Venta (TPV) para tomar pedidos y una pantalla de Sistema de Cocina (KDS).
    - **Agencias de Viajes**: Creación y gestión de paquetes turísticos y manejo de sus reservas.

6.  **Gestión Financiera Simplificada**:
    - **Costos (`/empresa/costos`)**: Registrar costos operativos para tener una visión de la rentabilidad.
    - **Precios (`/empresa/precios`)**: Definir reglas de precios dinámicos (ej. precios más altos en temporada alta o fines de semana).

### Para el Guía Turístico (Rol: `GuiaTuristico`):

1.  **Gestión de Perfil (`/guia/perfil`)**:
    - Crear y actualizar su perfil público con información sobre sus especialidades, idiomas que habla, tarifas y fotos.

2.  **Gestión de Reservas (`/guia/reservas`)**:
    - Ver y gestionar las reservas de tours que ha recibido de los turistas.

### Para el Administrador del Sistema (Roles: `SuperAdmin`, `AdminMunicipal`, `AdminDepartamental`):

1.  **Dashboard Administrativo (`/admin/dashboard`)**:
    - Vista general del estado del sistema: número de empresas registradas, usuarios activos, actividad reciente.

2.  **Gestión de Empresas (`/admin/empresas`)**:
    - Aprobar, rechazar, editar o desactivar los perfiles de las empresas y prestadores de servicios turísticos en la plataforma.

3.  **Gestión de Contenido General**:
    - Administrar el contenido público como los atractivos turísticos, noticias o eventos generales del territorio.
