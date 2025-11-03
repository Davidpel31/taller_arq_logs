import pika
import json
import time
import random

# Configuración de conexión a RabbitMQ
RABBITMQ_HOST = "rabbitmq"
EXCHANGE_NAME = "weather_exchange"
ROUTING_KEY = "weather.data"
QUEUE_NAME = "weather_queue"

def connect_rabbitmq():
    """Crea una conexión y canal con RabbitMQ, con reintento automático."""
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            channel = connection.channel()

            # Declarar exchange y cola durables
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct", durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=ROUTING_KEY)

            return connection, channel
        except Exception as e:
            print("Esperando que RabbitMQ esté disponible...", e)
            time.sleep(5)

def generate_weather_data():
    """Genera datos simulados de estación meteorológica."""
    return {
        "station_id": f"station_{random.randint(1,5)}",
        "temperature": round(random.uniform(-5, 45), 2),
        "humidity": round(random.uniform(10, 100), 2),
        "pressure": round(random.uniform(900, 1100), 2)
    }

if __name__ == "__main__":
    connection, channel = connect_rabbitmq()

    print("📡 Enviando datos meteorológicos...")
    while True:
        data = generate_weather_data()
        message = json.dumps(data)

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2  # Hace el mensaje persistente
            )
        )
        print(f"📤 Enviado: {message}")
        time.sleep(3)
