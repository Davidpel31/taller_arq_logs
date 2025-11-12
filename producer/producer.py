import pika
import json
import time
import random
from datetime import datetime
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de RabbitMQ
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_queue = os.getenv("RABBITMQ_QUEUE", "logs_queue")

# Rango válido de datos meteorológicos
TEMP_MIN, TEMP_MAX = 15, 35
HUMIDITY_MIN, HUMIDITY_MAX = 40, 90
STATION_MIN, STATION_MAX = 1, 5

def validar_datos(estacion_id, temperatura, humedad):
    """Valida los datos generados."""
    if not (STATION_MIN <= estacion_id <= STATION_MAX):
        raise ValueError(f"Estación inválida: {estacion_id}")
    if not (TEMP_MIN <= temperatura <= TEMP_MAX):
        raise ValueError(f"Temperatura inválida: {temperatura}")
    if not (HUMIDITY_MIN <= humedad <= HUMIDITY_MAX):
        raise ValueError(f"Humedad inválida: {humedad}")
    return True

def publicar_datos():
    """Publica datos meteorológicos a RabbitMQ."""
    max_retries = 5
    retry = 0
    
    while retry < max_retries:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq_host,
                    connection_attempts=5,
                    retry_delay=2
                )
            )
            channel = connection.channel()
            # Declarar exchange tipo 'topic' para routing por estación
            channel.exchange_declare(exchange='weather.data', exchange_type='topic', durable=True)
            # Declarar cola y (opcional) asegurar que exista
            channel.queue_declare(queue=rabbitmq_queue, durable=True)
            
            logger.info("✅ Conectado a RabbitMQ")
            
            while True:
                try:
                    estacion_id = random.randint(STATION_MIN, STATION_MAX)
                    temperatura = round(random.uniform(TEMP_MIN, TEMP_MAX), 2)
                    humedad = round(random.uniform(HUMIDITY_MIN, HUMIDITY_MAX), 2)
                    
                    # Validar datos
                    validar_datos(estacion_id, temperatura, humedad)
                    
                    log = {
                        "estacion_id": estacion_id,
                        "temperatura": temperatura,
                        "humedad": humedad,
                        "fecha": datetime.now().isoformat()
                    }
                    
                    routing_key = f"station.{estacion_id}"
                    channel.basic_publish(
                        exchange='weather.data',
                        routing_key=routing_key,
                        body=json.dumps(log),
                        properties=pika.BasicProperties(delivery_mode=2)  # Mensaje persistente
                    )
                    logger.info(f"📤 Enviado: {log}")
                    time.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Error generando datos: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Error de conexión a RabbitMQ: {e}")
            retry += 1
            if retry < max_retries:
                logger.info(f"Reintentando en 5 segundos... ({retry}/{max_retries})")
                time.sleep(5)
    
    logger.error(f"Máximo de reintentos alcanzado ({max_retries})")

if __name__ == "__main__":
    try:
        publicar_datos()
    except KeyboardInterrupt:
        logger.info("Productor detenido")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
