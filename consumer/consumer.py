import pika
import psycopg2
import json
import time

# Configuración de conexión
RABBITMQ_HOST = "rabbitmq"
POSTGRES_HOST = "postgres"
POSTGRES_DB = "weather_db"
POSTGRES_USER = "admin"
POSTGRES_PASSWORD = "admin123"

EXCHANGE_NAME = "weather_exchange"
QUEUE_NAME = "weather_queue"


def connect_postgres():
    """Conexión a PostgreSQL con reintentos."""
    while True:
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            conn.autocommit = True
            print("✅ Conectado a PostgreSQL")
            return conn
        except Exception as e:
            print("❌ Error al conectar a PostgreSQL, reintentando...", e)
            time.sleep(5)


def connect_rabbitmq():
    """Conexión a RabbitMQ con reintentos."""
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            channel = connection.channel()

            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_qos(prefetch_count=1)

            print("✅ Conectado a RabbitMQ")
            return connection, channel
        except Exception as e:
            print("❌ Esperando RabbitMQ...", e)
            time.sleep(5)


def save_to_db(conn, data):
    """Guarda los datos validados en la tabla weather_logs."""
    with conn.cursor() as cursor:
        cursor.execute("""
    INSERT INTO weather_logs (station_id, temperature, humidity, pressure, created_at)
    VALUES (%s, %s, %s, %s, NOW());
""", (data["station_id"], data["temperature"], data["humidity"], data["pressure"]))


def callback(ch, method, properties, body):
    """Procesa cada mensaje recibido."""
    try:
        data = json.loads(body)
        print(f"📩 Recibido: {data}")

        # Validación básica
        if not (-50 <= data["temperature"] <= 60):
            raise ValueError("Temperatura fuera de rango")
        if not (0 <= data["humidity"] <= 100):
            raise ValueError("Humedad fuera de rango")
        if not (850 <= data["pressure"] <= 1100):
            raise ValueError("Presión fuera de rango")

        save_to_db(conn, data)
        print("💾 Guardado en PostgreSQL")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"⚠️ Error procesando mensaje: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


if __name__ == "__main__":
    conn = connect_postgres()
    connection, channel = connect_rabbitmq()

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print("👂 Esperando mensajes...")
    channel.start_consuming()

