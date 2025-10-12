# Sistema de Gestión Turística Territorial

Este proyecto es una aplicación web para la gestión turística territorial, desarrollada con un backend en Django y un frontend en JavaScript como una Single Page Application (SPA).

## Requisitos del Entorno

*   Python 3.10+
*   Node.js 16+ (opcional, para herramientas de frontend)
*   PostgreSQL (recomendado para producción) o SQLite (para desarrollo)

## Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Configurar el Backend:**
    *   Navega al directorio `turismo_django`.
    *   Crea un entorno virtual:
        ```bash
        python -m venv venv
        source venv/bin/activate  # En Windows: venv\Scripts\activate
        ```
    *   Instala las dependencias de Python:
        ```bash
        pip install -r requirements.txt
        ```
    *   Crea un archivo `.env` a partir del `.env.example` y configúralo con tus valores:
        ```bash
        cp .env.example .env
        # Edita el archivo .env con tu SECRET_KEY y otras configuraciones
        ```
    *   Aplica las migraciones de la base de datos:
        ```bash
        python manage.py migrate
        ```

3.  **Configurar el Frontend:**
    *   El frontend no requiere un paso de construcción. Los archivos estáticos se sirven directamente desde el directorio `frontend`.

## Ejecución

1.  **Iniciar el servidor de Django:**
    *   Desde el directorio `turismo_django`, ejecuta:
        ```bash
        python manage.py runserver
        ```
    *   La aplicación estará disponible en `http://127.0.0.1:8000`.

## Variables de Entorno

El backend utiliza un archivo `.env` para gestionar la configuración. Basado en `.env.example`, estas son las variables principales:

*   `SECRET_KEY`: Una clave secreta y única para la instancia de Django.
*   `DEBUG`: `True` para desarrollo, `False` para producción.
*   `ALLOWED_HOSTS`: Una lista separada por comas de los hosts/dominios permitidos (ej: `127.0.0.1,localhost,yourdomain.com`).
*   `CORS_ALLOWED_ORIGINS`: Una lista separada por comas de los orígenes permitidos para las peticiones CORS (ej: `http://localhost:8000,http://127.0.0.1:8000`).

## Credenciales de Prueba

*   **SuperAdmin:**
    *   Usuario: `superadmin`
    *   Contraseña: `testpassword`
*   **Propietario de Empresa:**
    *   Usuario: `owner`
    *   Contraseña: `testpassword`
*   **Usuario Normal:**
    *   Usuario: `testuser`
    *   Contraseña: `testpassword`

## Estructura del Proyecto

*   `turismo_django/`: Contiene el proyecto de Django.
    *   `turismo_django/`: El directorio principal del proyecto Django.
        *   `api/`: La aplicación de Django que contiene los modelos, vistas, y serializadores de la API REST.
        *   `settings.py`: El archivo de configuración principal.
        *   `urls.py`: El enrutador de URLs principal.
    *   `manage.py`: El script de gestión de Django.
*   `frontend/`: Contiene la Single Page Application.
    *   `index.html`: El punto de entrada principal del frontend.
    *   `static/`: Contiene los archivos estáticos (CSS, JS, imágenes).
        *   `js/`: Contiene el código JavaScript modularizado.

## Explicación Técnica General

El backend está construido con Django y Django REST Framework, proporcionando una API RESTful para la gestión de todos los datos de la aplicación. Utiliza un sistema de autenticación basado en tokens y un modelo de usuario personalizado para la gestión de roles.

El frontend es una SPA escrita en JavaScript puro, que consume la API del backend. Gestiona el estado de la autenticación y renderiza dinámicamente las vistas según el rol del usuario.
