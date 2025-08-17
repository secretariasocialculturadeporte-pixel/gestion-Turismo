import logging
import os

# --- Configuración del Logger de Auditoría ---

# Crear el directorio de logs si no existe
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Crear un logger específico para la auditoría
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

# Crear un manejador de archivo que escriba en audit.log
audit_handler = logging.FileHandler(os.path.join(log_dir, 'audit.log'), encoding='utf-8')
audit_handler.setLevel(logging.INFO)

# Crear un formato para los logs de auditoría
# Formato: [Timestamp] [Nivel] [Usuario] [Acción] - [Detalles]
audit_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
audit_handler.setFormatter(audit_formatter)

# Añadir el manejador al logger, evitando duplicados
if not audit_logger.handlers:
    audit_logger.addHandler(audit_handler)

def log_audit(user_id: int, action: str, details: str):
    """
    Función helper para registrar un evento de auditoría.

    Args:
        user_id (int): El ID del usuario que realiza la acción.
        action (str): La acción realizada (e.g., 'CREATE_EMPRESA', 'UPDATE_USUARIO').
        details (str): Detalles relevantes de la acción (e.g., 'ID: 123, Nombre: Nuevo Hotel').
    """
    if user_id is None:
        user_id = "SYSTEM" # Para acciones no ligadas a un usuario logueado

    audit_logger.info(f"User:{user_id} | Action:{action} | Details: {details}")
