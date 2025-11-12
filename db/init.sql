-- Usar la base de datos ya creada por Docker (logsdb)
-- Crear tabla de logs
-- Tabla principal renombrada a weather_logs con constraints e índices
CREATE TABLE IF NOT EXISTS weather_logs (
    id SERIAL PRIMARY KEY,
    estacion_id INT NOT NULL CHECK (estacion_id > 0),
    temperatura NUMERIC(5,2) NOT NULL CHECK (temperatura BETWEEN  -100 AND 100),
    humedad NUMERIC(5,2) NOT NULL CHECK (humedad BETWEEN 0 AND 100),
    fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para consultas por estación y tiempo
CREATE INDEX IF NOT EXISTS idx_weather_logs_estacion_fecha ON weather_logs (estacion_id, fecha);

-- Tabla para mensajes fallidos (errores al procesar)
CREATE TABLE IF NOT EXISTS weather_logs_errors (
    id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    error_text TEXT,
    received_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

