# ⚙️ CONFIGURACIÓN AVANZADA - Tuning y Optimización

## 📋 Índice

1. [Variables de Entorno](#variables-de-entorno)
2. [Tuning de RabbitMQ](#tuning-de-rabbitmq)
3. [Tuning de PostgreSQL](#tuning-de-postgresql)
4. [Tuning de Python](#tuning-de-python)
5. [Escalabilidad](#escalabilidad)
6. [Monitoreo](#monitoreo)

---

## 🔧 Variables de Entorno

### Producer Configuration

```bash
# Intervalo entre mensajes (segundos)
PRODUCER_INTERVAL=5

# Rangos de datos meteorológicos
TEMP_MIN=15
TEMP_MAX=35
HUMIDITY_MIN=40
HUMIDITY_MAX=90
STATION_MIN=1
STATION_MAX=5

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_QUEUE=logs_queue
RABBITMQ_PORT=5672

# Reintentos
PRODUCER_RETRIES=5
PRODUCER_RETRY_DELAY=2
```

### Consumer Configuration

```bash
# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_QUEUE=logs_queue
RABBITMQ_PORT=5672

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=logsdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# QoS (Quality of Service)
RABBITMQ_PREFETCH_COUNT=1  # Procesar 1 mensaje a la vez

# Reintentos
CONSUMER_RETRIES=5
CONSUMER_RETRY_DELAY=3
```

---

## 🐇 Tuning de RabbitMQ

### Aumentar throughput (mensajes/segundo)

**docker-compose.yml:**
```yaml
rabbitmq:
  environment:
    # Aumentar límite de conexiones
    RABBITMQ_CHANNEL_MAX: 2048
    # Aumentar timeout
    RABBITMQ_HEARTBEAT: 60
```

**Consumer:**
```python
# Aumentar prefetch_count para procesar más mensajes
channel.basic_qos(prefetch_count=10)  # Por defecto: 1
```

### Persistencia de mensajes

**Producer:**
```python
# Mensajes persistentes (delivery_mode=2)
channel.basic_publish(
    exchange='',
    routing_key=rabbitmq_queue,
    body=json.dumps(log),
    properties=pika.BasicProperties(delivery_mode=2)  # Persisten en disco
)
```

### Configuración de cola durable

```python
# Cola durable (persiste después de reinicio)
channel.queue_declare(queue=rabbitmq_queue, durable=True)
```

---

## 🐘 Tuning de PostgreSQL

### Conexiones

**docker-compose.yml:**
```yaml
postgres:
  environment:
    # Máximo de conexiones simultáneas
    POSTGRES_INIT_ARGS: "-c max_connections=100"
    # Conexiones reservadas
    POSTGRES_INIT_ARGS: "-c superuser_reserved_connections=5"
```

### Performance

```yaml
postgres:
  environment:
    # Buffer compartido (25% de RAM recomendado)
    POSTGRES_INIT_ARGS: "-c shared_buffers=256MB"
    # Work memory (RAM por operación)
    POSTGRES_INIT_ARGS: "-c work_mem=10MB"
    # Maintenance work memory
    POSTGRES_INIT_ARGS: "-c maintenance_work_mem=64MB"
```

### Índices

```sql
-- Crear índices para consultas rápidas
CREATE INDEX idx_logs_estacion ON logs(estacion_id);
CREATE INDEX idx_logs_fecha ON logs(fecha);
CREATE INDEX idx_logs_fecha_estacion ON logs(fecha, estacion_id);
```

### Vacuum automático

```yaml
postgres:
  environment:
    # Autovacuum
    POSTGRES_INIT_ARGS: "-c autovacuum=on"
    POSTGRES_INIT_ARGS: "-c autovacuum_naptime=10s"
```

---

## 🐍 Tuning de Python

### Consumer - Pool de Conexiones

```python
# Implementar pool de conexiones (psycopg2)
from psycopg2 import pool

db_pool = pool.SimpleConnectionPool(
    1,        # Mínimo de conexiones
    10,       # Máximo de conexiones
    **postgres_config
)

# Obtener conexión del pool
conn = db_pool.getconn()

# Devolver al pool
db_pool.putconn(conn)
```

### Producer - Batch Publishing

```python
# Enviar múltiples mensajes en batch
messages = []
for i in range(100):
    messages.append({
        "estacion_id": random.randint(1, 5),
        "temperatura": round(random.uniform(15, 35), 2),
        "humedad": round(random.uniform(40, 90), 2),
        "fecha": datetime.now().isoformat()
    })

# Publicar en batch
for msg in messages:
    channel.basic_publish(
        exchange='',
        routing_key=rabbitmq_queue,
        body=json.dumps(msg),
        properties=pika.BasicProperties(delivery_mode=2)
    )
```

### Logging en Producción

```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

---

## 📈 Escalabilidad

### Horizontal Scaling - Múltiples Consumers

```bash
# Lanzar múltiples consumers
docker-compose up -d --scale consumer=3

# Ver estado
docker-compose ps
```

**docker-compose.yml mejorado:**
```yaml
consumer:
  build: ./consumer
  depends_on:
    postgres:
      condition: service_healthy
    rabbitmq:
      condition: service_healthy
  environment:
    RABBITMQ_HOST: rabbitmq
    RABBITMQ_QUEUE: logs_queue
  # Sin container_name para permitir múltiples instancias
  restart: on-failure:5
```

### Load Balancing

```yaml
# Con Traefik (para web services)
services:
  traefik:
    image: traefik:v2.10
    ports:
      - "80:80"
      - "8080:8080"
    
  web-api:
    build: ./api
    labels:
      - "traefik.http.routers.api.rule=Path(`/api`)"
```

---

## 🔍 Monitoreo

### Prometheus + Grafana

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15692']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

### Métricas Custom (Prometheus)

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# Métricas
messages_processed = Counter(
    'messages_processed_total',
    'Total de mensajes procesados',
    ['queue_name']
)

processing_time = Histogram(
    'message_processing_seconds',
    'Tiempo de procesamiento',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

# Usar en código
start_http_server(8000)  # Exponer en puerto 8000

@processing_time.time()
def callback(ch, method, properties, body):
    # Procesar mensaje
    messages_processed.labels(queue_name=rabbitmq_queue).inc()
```

---

## 📊 Queries SQL de Monitoreo

### Performance

```sql
-- Tablas más grandes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname != 'pg_catalog' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Consultas lentas
SELECT query, mean_exec_time, stddev_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC;

-- Índices no utilizados
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
AND indexname NOT IN (SELECT indexrelname FROM pg_stat_user_indexes);
```

### Health Check

```sql
-- Conexiones activas
SELECT count(*) as active_connections FROM pg_stat_activity;

-- Cache hit ratio
SELECT 
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit) as heap_hit,
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;

-- Vacío automático
SELECT schemaname, tablename, last_vacuum, last_autovacuum
FROM pg_stat_user_tables
ORDER BY last_vacuum DESC;
```

---

## 🚀 Checklist de Optimización

```
RABBITMQ
  ☐ Configurar durable queues
  ☐ Usar persistent messages
  ☐ Ajustar channel_max según carga
  ☐ Configurar heartbeat apropiadamente
  ☐ Implementar dead-letter queues

POSTGRESQL
  ☐ Crear índices apropiados
  ☐ Ajustar shared_buffers
  ☐ Configurar autovacuum
  ☐ Implementar particionamiento (si es necesario)
  ☐ Usar VACUUM ANALYZE regularmente

PYTHON
  ☐ Implementar connection pooling
  ☐ Usar batch processing
  ☐ Configurar logging estructurado
  ☐ Implementar circuit breaker
  ☐ Agregar métricas Prometheus

INFRASTRUCTURE
  ☐ Horizontal scaling (múltiples consumers)
  ☐ Load balancing
  ☐ Monitoring y alerting
  ☐ Backup y recovery
  ☐ Disaster recovery plan
```

---

## 📈 Benchmarking

### Prueba de Carga

```bash
# Usando Apache Bench (para APIs)
ab -n 1000 -c 10 http://localhost:8000/

# Usando wrk (para HTTP)
wrk -t4 -c100 -d30s http://localhost:8000/

# Usando locust (Python)
locust -f locustfile.py --host=http://localhost:8000
```

### Monitoreo durante tests

```bash
# Terminal 1: Monitoreo de recursos
watch -n 1 'docker stats --no-stream'

# Terminal 2: Logs del consumer
docker logs -f consumer

# Terminal 3: Consultas a BD
docker exec postgres psql -U postgres -d logsdb -c "SELECT COUNT(*) FROM logs;" --interval 1
```

---

## 🔐 Seguridad en Producción

### Variables Sensibles

```bash
# .env (no versionado)
POSTGRES_PASSWORD=secure_password_here
RABBITMQ_PASSWORD=secure_password_here
API_KEY=secret_key_here
```

### SSL/TLS

```yaml
rabbitmq:
  environment:
    RABBITMQ_SSL_VERIFY: verify_peer
    RABBITMQ_SSL_CACERTFILE: /etc/rabbitmq/certs/ca_certificate.pem
    RABBITMQ_SSL_CERTFILE: /etc/rabbitmq/certs/server_certificate.pem
    RABBITMQ_SSL_KEYFILE: /etc/rabbitmq/certs/server_key.pem
```

### Autenticación

```python
# RabbitMQ con autenticación
credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=host,
        credentials=credentials,
        ssl_options=pika.SSLOptions(context)
    )
)
```

---

## 🎓 Recursos Adicionales

- [RabbitMQ Best Practices](https://www.rabbitmq.com/bestpractices.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python pika Documentation](https://pika.readthedocs.io/)
- [Docker Compose Best Practices](https://docs.docker.com/compose/compose-file/)

---

**Documento de configuración avanzada ✅**
