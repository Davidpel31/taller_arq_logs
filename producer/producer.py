import pika
import json
import time
import random
from datetime import datetime
import os
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_queue = os.getenv("RABBITMQ_QUEUE", "logs_queue")

TEMP_MIN, TEMP_MAX = 15, 35
HUMIDITY_MIN, HUMIDITY_MAX = 40, 90
STATION_MIN, STATION_MAX = 1, 5


METRICS_INTERVAL = 30  

metrics = {
    "messages_sent": 0,
    "validation_errors": 0,
    "publish_errors": 0,
    "connection_errors": 0,
    "retries": 0,
    "total_publish_time": 0.0,
    "start_time": time.time(),
    "last_metrics_log": time.time(),
}


def log_metrics():
    """Imprime un resumen de métricas de rendimiento en el log."""
    now = time.time()
    elapsed = now - metrics["start_time"]
    if elapsed <= 0:
        elapsed = 1 

    msg_per_second = metrics["messages_sent"] / elapsed
    avg_publish_time = (
        metrics["total_publish_time"] / metrics["messages_sent"]
        if metrics["messages_sent"] > 0
        else 0.0
    )

    logger.info(
        (
            "📊 [MÉTRICAS PRODUCER] msgs_enviados=%d | msg/s=%.2f | "
            "tiempo_promedio_publicación=%.4fs | "
            "errores_validación=%d | errores_publicación=%d | "
            "errores_conexión=%d | reintentos=%d | tiempo_total=%.1fs"
        ),
        metrics["messages_sent"],
        msg_per_second,
        avg_publish_time,
        metrics["validation_errors"],
        metrics["publish_errors"],
        metrics["connection_errors"],
        metrics["retries"],
        elapsed,
    )

    metrics["last_metrics_log"] = now


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

            channel.exchange_declare(
                exchange='weather.data',
                exchange_type='topic',
                durable=True
            )

            logger.info("Conectado a RabbitMQ")
            retry = 0  

            while True:
                try:
                    estacion_id = random.randint(STATION_MIN, STATION_MAX)
                    temperatura = round(random.uniform(TEMP_MIN, TEMP_MAX), 2)
                    humedad = round(random.uniform(HUMIDITY_MIN, HUMIDITY_MAX), 2)

                    # VALIDACION METRICA
                    try:
                        validar_datos(estacion_id, temperatura, humedad)
                    except ValueError as ve:
                        metrics["validation_errors"] += 1
                        logger.warning(f"Datos inválidos: {ve}")
                        time.sleep(1)
                        continue  # no publicamos este mensaje

                    log = {
                        "estacion_id": estacion_id,
                        "temperatura": temperatura,
                        "humedad": humedad,
                        "fecha": datetime.now().isoformat()
                    }

                    routing_key = f"station.{estacion_id}"

                   
                    t0 = time.perf_counter()
                    channel.basic_publish(
                        exchange='weather.data',
                        routing_key=routing_key,
                        body=json.dumps(log),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    publish_time = time.perf_counter() - t0

                    metrics["messages_sent"] += 1
                    metrics["total_publish_time"] += publish_time

                    logger.info(
                        f"📤 Enviado: {log} (publish_time={publish_time:.5f}s)"
                    )

                    now = time.time()
                    if now - metrics["last_metrics_log"] >= METRICS_INTERVAL:
                        log_metrics()

                    time.sleep(5)

                except Exception as e:
                    metrics["publish_errors"] += 1
                    logger.error(f"Error generando/publicando datos: {e}")
                    time.sleep(1)

        except Exception as e:
            metrics["connection_errors"] += 1
            retry += 1
            metrics["retries"] = retry
            logger.error(f"Error de conexión a RabbitMQ: {e}")
            if retry < max_retries:
                logger.info(f"Reintentando en 5 segundos... ({retry}/{max_retries})")
                time.sleep(5)

    logger.error(f"Máximo de reintentos alcanzado ({max_retries})")
    log_metrics()  


if __name__ == "__main__":
    try:
        publicar_datos()
    except KeyboardInterrupt:
        logger.info("Productor detenido por el usuario")
        log_metrics()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        log_metrics()
