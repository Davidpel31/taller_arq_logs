import time
import psycopg2
import os

# Configuración de conexión a PostgreSQL
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

# Último id leído
last_id = 0

while True:
    try:
        # Traer nuevos logs desde la última lectura
        cur.execute(
            "SELECT id, estacion_id, temperatura, humedad, timestamp FROM logs WHERE id > %s ORDER BY id ASC",
            (last_id,)
        )
        rows = cur.fetchall()
        for row in rows:
            print(f"[Consumer] Nuevo log: {row}", flush=True)
            last_id = row[0]  # Actualizar el último id leído
    except Exception as e:
        print(f"[Consumer] Error al leer logs: {e}", flush=True)
        conn.rollback()  # Reinicia la transacción si hay error

    time.sleep(5)  # Esperar 5 segundos antes de consultar de nuevo

