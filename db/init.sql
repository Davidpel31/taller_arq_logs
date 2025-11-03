CREATE TABLE IF NOT EXISTS weather_logs (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL,
    temperature NUMERIC(5,2) NOT NULL,
    humidity NUMERIC(5,2) NOT NULL,
    pressure NUMERIC(6,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

