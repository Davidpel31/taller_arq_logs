import pika
import json
import psycopg2
import os
import time
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

# Configuración de PostgreSQL
postgres_config = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "database": os.getenv("POSTGRES_DB", "logsdb"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "connect_timeout": 5,
}

db_connection = None

def conectar_postgres():
    """Establece conexión persistente con PostgreSQL."""
    global db_connection
    while True:
        try:
            db_connection = psycopg2.connect(**postgres_config)
            logger.info("✅ Conexión establecida con PostgreSQL")
            return db_connection
        except Exception as e:
            logger.error(f"Error al conectar a PostgreSQL: {e}")
            time.sleep(3)

def validar_conexion():
    """Verifica si la conexión está activa, si no, reconecta."""
    global db_connection
    try:
        if db_connection and not db_connection.closed:
            db_connection.isolation_level  # Test de conexión
            return db_connection
    except:
        pass
    return conectar_postgres()

def callback(ch, method, properties, body):
    """Procesa mensajes de la cola RabbitMQ."""
    try:
        data = json.loads(body)
        
        # Validar datos
        if not all(key in data for key in ["estacion_id", "temperatura", "humedad", "fecha"]):
            logger.warning(f"⚠️ Datos incompletos: {data}")
            return
        
        # Obtener conexión válida
        conn = validar_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO logs (estacion_id, temperatura, humedad, fecha)
            VALUES (%s, %s, %s, %s)
        """, (data["estacion_id"], data["temperatura"], data["humedad"], data["fecha"]))
        conn.commit()
        logger.info(f"💾 Insertado en BD: {data}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decodificando JSON: {e}")
    except Exception as e:
        logger.error(f"Error al insertar dato: {e}")

def consumir():
    """Inicia el consumidor de mensajes."""
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
            channel.queue_declare(queue=rabbitmq_queue, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)
            
            logger.info("📥 Esperando mensajes...")
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
    except Exception as e:
        logger.error(f"Error fatal: {e}")

