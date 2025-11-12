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
            # Rechazar el mensaje para que pueda ir a DLQ si está configurado
            try:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception:
                logger.warning("No se pudo basic_nack tras datos incompletos")
            return
        
        # Obtener conexión válida
        conn = validar_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO weather_logs (estacion_id, temperatura, humedad, fecha)
                VALUES (%s, %s, %s, %s)
            """, (data["estacion_id"], data["temperatura"], data["humedad"], data["fecha"]))
            conn.commit()
            logger.info(f"💾 Insertado en BD: {data}")
            # ACK manual tras persistir en DB
            try:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                logger.warning("No se pudo hacer basic_ack (posible conexión cerrada)")
        except Exception as e:
            # Si hay error en la transacción, hacer rollback para limpiar el estado
            try:
                conn.rollback()
            except Exception:
                logger.warning("No se pudo hacer rollback en la conexión a la DB")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decodificando JSON: {e}")
        # Rechazar y enviar a DLQ (si existe)
        try:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception:
            logger.warning("No se pudo basic_nack tras JSONDecodeError")
    except Exception as e:
        logger.error(f"Error al insertar dato: {e}")
        # Rechazar mensaje para que no se reencole (irá a DLX si está configurado)
        try:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception:
            logger.warning("No se pudo basic_nack tras excepción")

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
            # Declarar exchange principal (topic) y DLX (dead-letter exchange)
            channel.exchange_declare(exchange='weather.data', exchange_type='topic', durable=True)
            channel.exchange_declare(exchange='weather.dlx', exchange_type='fanout', durable=True)

            # Declarar cola principal con DLX asociado
            args = {
                'x-dead-letter-exchange': 'weather.dlx'
            }
            channel.queue_declare(queue=rabbitmq_queue, durable=True, arguments=args)
            # Enlazar la cola al exchange por patrón station.*
            channel.queue_bind(queue=rabbitmq_queue, exchange='weather.data', routing_key='station.*')

            # Declarar la cola de DLQ y bind a la exchange DLX
            channel.queue_declare(queue='logs_dlx', durable=True)
            channel.queue_bind(queue='logs_dlx', exchange='weather.dlx')

            channel.basic_qos(prefetch_count=1)
            # Usar ack manual para garantizar entrega
            channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=False)
            
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

