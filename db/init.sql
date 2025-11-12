-- Usar la base de datos ya creada por Docker (logsdb)
-- Crear tabla de logs
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    estacion_id INT NOT NULL,
    temperatura DECIMAL(5,2),
    humedad DECIMAL(5,2),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

