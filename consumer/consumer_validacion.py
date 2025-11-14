import json
import logging

logger = logging.getLogger(__name__)

CAMPOS_REQUERIDOS = ["estacion_id", "temperatura", "humedad", "fecha"]

def validar_mensaje(body):
    
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"Error decodificando JSON: {e}")
        return None, "json_error"

    if not all(campo in data for campo in CAMPOS_REQUERIDOS):
        logger.warning(f"Datos incompletos: {data}")
        return None, "campos_incompletos"

    return data, None
