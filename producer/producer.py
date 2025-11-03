import time
import random
import psycopg2
import os

# Configuración de conexión a PostgreSQL desde variables de entorno o por defecto
DB_HOST = os.getenv("DATABASE_HOST", "postgres")
DB_PORT = int(os.getenv("DATABASE_PORT", 5432))
DB_USER = os.getenv("DATABASE_USER", "admin")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "admin123")
DB_NAME = os.getenv("DATABASE_NAME", "weather_db")

# Esperar hasta que PostgreSQL esté listo
while True:
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cur = conn.cursor()
        print("Conexión establecida con PostgreSQL", flush=True)
        break
    except Exception as e:
        print(f"Error al conectar a PostgreSQL: {e}. Reintentando en 3 segundos...", flush=True)
        time.sleep(3)

# Bucle principal de envío de datos
while True:
    estacion_id = random.randint(1, 5)
    temperatura = round(random.uniform(20, 35), 2)
    humedad = round(random.uniform(30, 80), 2)

    try:
        cur.execute(
            "INSERT INTO logs (estacion_id, temperatura, humedad) VALUES (%s, %s, %s)",
            (estacion_id, temperatura, humedad)
        )
        conn.commit()
        print(f"[Producer] Dato enviado: estacion_id={estacion_id}, temperatura={temperatura}, humedad={humedad}", flush=True)
    except Exception as e:
        print(f"[Producer] Error al insertar dato: {e}", flush=True)
        conn.rollback()  # Reinicia la transacción para poder seguir insertando

    time.sleep(5)  # Esperar 5 segundos antes de enviar el siguiente dato

