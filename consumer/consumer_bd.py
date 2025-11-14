import psycopg2
import os
import time
import logging

logger = logging.getLogger(__name__)

postgres_config = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "database": os.getenv("POSTGRES_DB", "logsdb"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "connect_timeout": 5,
}

db_connection = None

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
    except Exception:
        pass
    return conectar_postgres()

def insertar_weather_log(data):
    
    conn = validar_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO weather_logs (estacion_id, temperatura, humedad, fecha)
            VALUES (%s, %s, %s, %s)
            """,
            (data["estacion_id"], data["temperatura"],
             data["humedad"], data["fecha"])
        )
        conn.commit()
        logger.info(f"Insertado en BD: {data}")
        return True
    except Exception as e:
        logger.error(f"Error al insertar dato: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        try:
            cursor.close()
        except Exception:
            pass
