import pika
import json
import psycopg2
import os
import time
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_queue = os.getenv("RABBITMQ_QUEUE", "logs_queue")


postgres_config = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "database": os.getenv("POSTGRES_DB", "logsdb"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "connect_timeout": 5,
}

db_connection = None


METRICS_INTERVAL = 30  

metrics = {
    "messages_received": 0,
    "db_ok": 0,
    "db_errors": 0,
    "json_errors": 0,
    "total_processing_time": 0.0,
    "start_time": time.time(),
    "last_log": time.time()
}

def log_metrics():
    """Imprime métricas de rendimiento del consumidor."""
    now = time.time()
    elapsed = now - metrics["start_time"]
    if elapsed <= 0:
        elapsed = 1

    msg_per_sec = metrics["messages_received"] / elapsed
    avg_proc_time = (
        metrics["total_processing_time"] / metrics["messages_received"]
        if metrics["messages_received"] > 0 else 0
    )

    logger.info(
        "[MÉTRICAS CONSUMER] "
        f"msgs_recibidos={metrics['messages_received']} | "
        f"msg/s={msg_per_sec:.3f} | "
        f"tiempo_promedio_proc={avg_proc_time:.5f}s | "
        f"db_ok={metrics['db_ok']} | "
        f"db_errores={metrics['db_errors']} | "
        f"json_errores={metrics['json_errors']} | "
        f"tiempo_total={elapsed:.1f}s"
    )

    metrics["last_log"] = now


def conectar_postgres():
    global db_connection
    while True:
        try:
            db_connection = psycopg2.connect(**postgres_config)
            logger.info("Conexión establecida con PostgreSQL")
            return db_connection
        except Exception as e:
            logger.error(f"Error al conectar a PostgreSQL: {e}")
            time.sleep(3)

def validar_conexion():
    global db_connection
    try:
        if db_connection and not db_connection.closed:
            db_connection.isolation_level
            return db_connection
    except:
        pass
    return conectar_postgres()


def callback(ch, method, properties, body):
    start = time.perf_counter()
    metrics["messages_received"] += 1

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        metrics["json_errors"] += 1
        logger.error(f"Error decodificando JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

 
    if not all(key in data for key in ["estacion_id", "temperatura", "humedad", "fecha"]):
        logger.warning(f"Datos incompletos: {data}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    conn = validar_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO weather_logs (estacion_id, temperatura, humedad, fecha)
            VALUES (%s, %s, %s, %s)
            """,
            (data["estacion_id"], data["temperatura"], data["humedad"], data["fecha"])
        )
        conn.commit()

        metrics["db_ok"] += 1
        logger.info(f"Insertado en BD: {data}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        metrics["db_errors"] += 1
        logger.error(f"Error al insertar dato: {e}")

        try:
            conn.rollback()
        except:
            pass

        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    finally:
        try:
            cursor.close()
        except:
            pass

   
    elapsed = time.perf_counter() - start
    metrics["total_processing_time"] += elapsed


    now = time.time()
    if now - metrics["last_log"] >= METRICS_INTERVAL:
        log_metrics()

def consumir():
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

            channel.exchange_declare(exchange='weather.data', exchange_type='topic', durable=True)
            channel.exchange_declare(exchange='weather.dlx', exchange_type='fanout', durable=True)

            args = {
                'x-dead-letter-exchange': 'weather.dlx'
            }

            channel.queue_declare(queue=rabbitmq_queue, durable=True, arguments=args)
            channel.queue_bind(queue=rabbitmq_queue, exchange='weather.data', routing_key='station.*')

            channel.queue_declare(queue='logs_dlx', durable=True)
            channel.queue_bind(queue='logs_dlx', exchange='weather.dlx')

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=False)

            logger.info("Esperando mensajes...")
            channel.start_consuming()

        except Exception as e:
            logger.error(f"Error en consumidor: {e}")
            retry += 1
            if retry < max_retries:
                logger.info(f"Reintentando en 5 segundos... ({retry}/{max_retries})")
                time.sleep(5)

    logger.error(f"Máximo de reintentos alcanzado ({max_retries})")

if __name__ == "__main__":
    try:
        conectar_postgres()
        consumir()
    except KeyboardInterrupt:
        logger.info("Consumidor detenido")
        if db_connection:
            db_connection.close()
