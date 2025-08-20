from langchain_core.tools import tool
from typing import Any, List, Dict

class ComunicacionesSoldiers:
    """
    El arsenal de herramientas de ejecución (la escuadra de Soldados) para las
    operaciones de Comunicación. Son comandados por el Sargento de Comunicaciones.
    """
    def __init__(self, api_client: Any):
        # En una aplicación real, este sería el cliente de la API de Notificaciones
        # y Comunicación. ej. self.api = CommunicationServices(db_session)
        self.api = api_client

    # --- Soldado #1: Soldado_Notificaciones (SNAT) ---
    @tool
    def enviar_notificacion_en_app(self, usuario_id: int, mensaje: str, tipo: str = "info", url_destino: str = None) -> Dict:
        """
        (SOLDADO NOTIFICACIONES - SNAT) Ejecuta el envío de una notificación en tiempo
        real a un usuario DENTRO de la plataforma (ej. un ícono de campana). El 'tipo'
        puede ser 'info', 'exito', 'advertencia', 'error'. La 'url_destino' es opcional,
        para que la notificación sea clickeable.
        """
        print(f"--- 💥 SOLDADO (SNAT): ¡ACCIÓN! Enviando notificación en-app tipo '{tipo}' al usuario {usuario_id}. ---")
        # result = self.api.send_in_app_notification(
        #     user_id=usuario_id,
        #     message=mensaje,
        #     type=tipo,
        #     target_url=url_destino
        # )
        # return result
        # Debería devolver algo como {"status": "success", "notification_id": "snat-998877"}
        return {"status": "success", "notification_id": "snat-998877", "message": f"Notificación en-app enviada."}

    # --- Soldado #2: Soldado_Recordatorios ---
    @tool
    def programar_recordatorio_push(self, usuario_id: int, mensaje: str, fecha_hora_envio: str) -> Dict:
        """
        (SOLDADO RECORDATORIOS) Ejecuta la programación de una notificación PUSH para
        una fecha y hora futuras (formato ISO 8601, ej: '2024-12-24T18:00:00Z').
        Es ideal para recordar clases, eventos o pagos pendientes.
        """
        print(f"--- 💥 SOLDADO (Recordatorios): ¡ACCIÓN! Programando recordatorio PUSH para usuario {usuario_id} en fecha {fecha_hora_envio}. ---")
        # result = self.api.schedule_push_reminder(
        #     user_id=usuario_id,
        #     message=mensaje,
        #     schedule_time=fecha_hora_envio
        # )
        # return result
        # Debería devolver algo como {"status": "scheduled", "reminder_id": "rem-push-12345"}
        return {"status": "scheduled", "reminder_id": "rem-push-12345", "message": f"Recordatorio PUSH programado."}

    # --- Soldado #3: Soldado_Mensajería_Interna ---
    @tool
    def enviar_mensaje_interno_chat(self, remitente_id: int, destinatario_id: int, mensaje: str) -> Dict:
        """
        (SOLDADO MENSAJERÍA) Ejecuta el envío de un mensaje a través del sistema de
        chat interno de la plataforma, de un usuario a otro (ej. de un instructor a
        un estudiante).
        """
        print(f"--- 💥 SOLDADO (Mensajería): ¡ACCIÓN! Enviando mensaje interno de {remitente_id} al destinatario {destinatario_id}. ---")
        # result = self.api.send_internal_chat_message(
        #     sender_id=remitente_id,
        #     recipient_id=destinatario_id,
        #     message=mensaje
        # )
        # return result
        # Debería devolver {"status": "sent", "message_id": "msg-int-67890"}
        return {"status": "sent", "message_id": "msg-int-67890", "message": f"Mensaje interno enviado."}

    # --- Soldado #4: Soldado_Enviar_Email_Masivo_Segmento ---
    @tool
    def enviar_email_a_segmento(self, id_segmento: str, asunto: str, cuerpo_html: str) -> Dict:
        """
        (SOLDADO EMAIL MASIVO) Ejecuta el envío de una campaña de email a un segmento
        de usuarios predefinido (ej. 'estudiantes-activos', 'inscritos-taller-salsa').
        """
        print(f"--- 💥 SOLDADO (Email Masivo): ¡ACCIÓN! Enviando email con asunto '{asunto}' al segmento '{id_segmento}'. ---")
        # result = self.api.send_bulk_email_to_segment(
        #     segment_id=id_segmento,
        #     subject=asunto,
        #     body_html=cuerpo_html
        # )
        # return result
        # Debería devolver {"status": "queued", "campaign_id": "camp-email-554433"}
        return {"status": "queued", "campaign_id": "camp-email-554433", "message": "Campaña de email encolada para envío."}

    # --- Soldado #5: Soldado_Enviar_SMS_Masivo_Segmento ---
    @tool
    def enviar_sms_a_segmento(self, id_segmento: str, mensaje_corto: str) -> Dict:
        """
        (SOLDADO SMS MASIVO) Ejecuta el envío de un mensaje de texto (SMS) masivo a
        todos los usuarios de un segmento predefinido que hayan dado su consentimiento.
        """
        print(f"--- 💥 SOLDADO (SMS Masivo): ¡ACCIÓN! Enviando SMS al segmento '{id_segmento}'. ---")
        # result = self.api.send_bulk_sms_to_segment(
        #     segment_id=id_segmento,
        #     short_message=mensaje_corto
        # )
        # return result
        # Debería devolver {"status": "queued", "campaign_id": "camp-sms-221100"}
        return {"status": "queued", "campaign_id": "camp-sms-221100", "message": "Campaña de SMS encolada para envío."}


    def get_all_soldiers(self) -> List:
        """
        Recluta y devuelve la Escuadra de Comunicaciones completa, lista para ser
        comandada por el Sargento de Comunicaciones.
        """
        return [
            self.enviar_notificacion_en_app,
            self.programar_recordatorio_push,
            self.enviar_mensaje_interno_chat,
            self.enviar_email_a_segmento,
            self.enviar_sms_a_segmento
        ]
