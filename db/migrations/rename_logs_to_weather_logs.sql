-- Migration: rename logs -> weather_logs or migrate data if both exist
-- Safe script: will either rename the table or copy rows then drop original

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'logs') THEN
        -- If weather_logs does not exist, rename table
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'weather_logs') THEN
            RAISE NOTICE 'Renaming table logs -> weather_logs';
            ALTER TABLE public.logs RENAME TO weather_logs;
            -- Attempt to add sensible constraints/indexes if columns exist
            BEGIN
                ALTER TABLE weather_logs ALTER COLUMN fecha SET DEFAULT CURRENT_TIMESTAMP;
            EXCEPTION WHEN undefined_column THEN
                RAISE NOTICE 'Column fecha not present or cannot alter default';
            END;
            BEGIN
                CREATE INDEX IF NOT EXISTS idx_weather_logs_estacion_fecha ON weather_logs (estacion_id, fecha);
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Could not create index idx_weather_logs_estacion_fecha';
            END;
        ELSE
            RAISE NOTICE 'weather_logs exists; inserting rows from logs into weather_logs and dropping logs';
            -- Copy rows that are not yet present
            INSERT INTO weather_logs (estacion_id, temperatura, humedad, fecha)
            SELECT l.estacion_id, l.temperatura, l.humedad, l.fecha
            FROM public.logs l
            LEFT JOIN weather_logs w ON w.estacion_id = l.estacion_id AND w.fecha = l.fecha
            WHERE w.id IS NULL;
            RAISE NOTICE 'Copied rows from logs to weather_logs. Now dropping logs';
            DROP TABLE public.logs;
        END IF;
    ELSE
        RAISE NOTICE 'Table logs does not exist; nothing to do.';
    END IF;
END
$$;

-- Ensure error table exists
CREATE TABLE IF NOT EXISTS weather_logs_errors (
    id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    error_text TEXT,
    received_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ensure index exists
CREATE INDEX IF NOT EXISTS idx_weather_logs_estacion_fecha ON weather_logs (estacion_id, fecha);
