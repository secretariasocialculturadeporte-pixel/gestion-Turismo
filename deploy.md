# Guía de Despliegue

Esta es una guía rápida para desplegar el Sistema de Gestión Turística Territorial en un entorno de producción.

## Requisitos Previos

*   Un servidor con Python 3.10+ instalado.
*   Una base de datos (se recomienda PostgreSQL).
*   Un servidor web (como Nginx o Apache).
*   Un servidor de aplicaciones WSGI (como Gunicorn o uWSGI).

## Pasos de Despliegue

1.  **Preparar el Entorno:**
    *   Clona el repositorio en tu servidor.
    *   Crea y activa un entorno virtual de Python.
    *   Instala las dependencias: `pip install -r requirements.txt`.

2.  **Configurar las Variables de Entorno:**
    *   Crea un archivo `.env` en el directorio `turismo_django`.
    *   Define las siguientes variables de entorno en el archivo `.env`:
        *   `SECRET_KEY`: Una clave secreta larga y aleatoria.
        *   `DEBUG=False`
        *   `ALLOWED_HOSTS`: El dominio de tu aplicación (ej: `yourdomain.com,www.yourdomain.com`).
        *   `CORS_ALLOWED_ORIGINS`: La URL de tu frontend (ej: `https://yourdomain.com`).
        *   Configura las variables de la base de datos (`DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).

3.  **Preparar la Aplicación Django:**
    *   Aplica las migraciones de la base de datos:
        ```bash
        python manage.py migrate
        ```
    *   Recopila los archivos estáticos:
        ```bash
        python manage.py collectstatic
        ```
    *   Crea un superusuario de Django (opcional, si necesitas acceso al admin de Django):
        ```bash
        python manage.py createsuperuser
        ```

4.  **Configurar Gunicorn (Servidor de Aplicaciones):**
    *   Instala Gunicorn: `pip install gunicorn`.
    *   Crea un servicio de systemd para Gunicorn para que se ejecute en segundo plano y se reinicie automáticamente. Ejemplo de un archivo de servicio (`gunicorn.service`):
        ```ini
        [Unit]
        Description=gunicorn daemon
        After=network.target

        [Service]
        User=<your-user>
        Group=<your-group>
        WorkingDirectory=/path/to/your/project/turismo_django
        ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind unix:/path/to/your/project/turismo_django.sock turismo_django.wsgi:application

        [Install]
        WantedBy=multi-user.target
        ```
    *   Inicia y habilita el servicio de Gunicorn:
        ```bash
        sudo systemctl start gunicorn
        sudo systemctl enable gunicorn
        ```

5.  **Configurar Nginx (Servidor Web):**
    *   Instala Nginx: `sudo apt-get install nginx`.
    *   Crea un archivo de configuración de Nginx para tu sitio. Ejemplo (`/etc/nginx/sites-available/yourdomain`):
        ```nginx
        server {
            listen 80;
            server_name yourdomain.com www.yourdomain.com;

            location = /favicon.ico { access_log off; log_not_found off; }
            location /static/ {
                root /path/to/your/project/turismo_django;
            }

            location / {
                include proxy_params;
                proxy_pass http://unix:/path/to/your/project/turismo_django.sock;
            }
        }
        ```
    *   Habilita el sitio y reinicia Nginx:
        ```bash
        sudo ln -s /etc/nginx/sites-available/yourdomain /etc/nginx/sites-enabled
        sudo systemctl restart nginx
        ```

## Consideraciones Adicionales

*   **HTTPS:** Configura un certificado SSL/TLS (por ejemplo, con Let's Encrypt) en Nginx para servir tu aplicación a través de HTTPS.
*   **Archivos Estáticos del Frontend:** Asegúrate de que tu servidor web (Nginx) esté configurado para servir los archivos del directorio `frontend/static`.
