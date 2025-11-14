# Guía de Uso - Sistema de Logs con RabbitMQ y PostgreSQL



- **Docker Desktop** instalado y ejecutándose
- **Git** (opcional)
- **DBeaver** o similar (opcional, para inspeccionar BD)

---

## Inicio Rápido

### Levantar todos los servicios

Desde la carpeta raíz del proyecto (`C:\taller_arq_logs`):

```bash
docker compose up -d
```

**Esto levantará:**
-  PostgreSQL (puerto 5432)
- RabbitMQ (puertos 5672, 15672)
- Producer (generador de datos)
- Consumer (procesador de datos)

**Si hiciste cambios en el código, usa:**
```bash
docker compose up --build -d
```

---

## 2️⃣ Verificar que todo está corriendo

```bash
docker ps
```

Deberías ver 4 contenedores corriendo:
- `postgres`
- `rabbitmq`
- `producer`
- `consumer`

---

## Panel de RabbitMQ

 **URL:** http://localhost:15672

**Credenciales:**
- Usuario: `guest`
- Contraseña: `guest`

**Qué puedes ver ahí:**
- Exchanges (donde el productor publica)
- Queues (colas de mensajes)
- Bindings (conexiones entre exchanges y colas)
- Estadísticas de mensajes procesados

---

##  Acceder a PostgreSQL

**Conexión desde DBeaver o cualquier cliente SQL:**

| Campo | Valor |
|-------|-------|
| **Host** | localhost |
| **Puerto** | 5432 |
| **Base de Datos** | logsdb |
| **Usuario** | postgres |
| **Contraseña** | postgres |

**Desde terminal:**
```bash
docker exec -it postgres psql -U postgres -d logsdb
```

---

## Consultar datos en PostgreSQL

### Conectarse al contenedor:
```bash
docker exec -it postgres psql -U postgres -d logsdb
```

### Ver estructura de tablas:
```sql
\dt
```

### Ver últimos 10 registros:
```sql
SELECT * FROM weather_logs ORDER BY id DESC LIMIT 10;
```

### Contar registros insertados:
```sql
SELECT COUNT(*) FROM weather_logs;
```

### Ver estadísticas por estación:
```sql
SELECT 
    estacion_id,
    COUNT(*) as registros,
    AVG(temperatura) as temp_promedio,
    AVG(humedad) as humedad_promedio
FROM weather_logs
GROUP BY estacion_id
ORDER BY estacion_id;
```

---

## Ver los logs de los servicios

### Logs en tiempo real del productor:
```bash
docker logs -f producer
```

### Logs en tiempo real del consumidor:
```bash
docker logs -f consumer
```

### Logs de PostgreSQL:
```bash
docker logs -f postgres
```

### Logs de RabbitMQ:
```bash
docker logs -f rabbitmq
```

---

## Detener los servicios

### Detener sin eliminar volúmenes (datos persisten):
```bash
docker compose down
```

### Detener y eliminar todo (incluyendo datos):
```bash
docker compose down -v
```

---

## Troubleshooting

### Los contenedores no inician
```bash

docker logs <nombre_contenedor>

docker compose down -v
docker compose up --build -d
```

### Errores de conexión a PostgreSQL
```bash

docker exec postgres pg_isready -U postgres

```bash

docker logs producer

docker logs consumer
```

### Deseas resetear todo
```bash
docker compose down -v
docker compose up --build -d
```

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Compose                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  PRODUCER           RABBITMQ          CONSUMER         │
│  ┌─────────┐      ┌─────────┐      ┌────────┐         │
│  │Generate │      │ Broker  │      │Process │         │
│  │ Datos   │─────►│ Queue   │─────►│  Data  │         │
│  │Aleatorios      │logs_q   │      │        │         │
│  └─────────┘      └─────────┘      └────────┘         │
│                                           │             │
│                                           ▼             │
│                                      ┌─────────┐        │
│                                      │PostgreSQL       │
│                                      │  logsdb  │       │
│                                      │  (logs)  │       │
│                                      └─────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos

1. **Producer** genera datos meteorológicos cada 5 segundos:
   - `estacion_id`: 1-5
   - `temperatura`: 15-35°C
   - `humedad`: 40-90%
   - `fecha`: timestamp ISO

2. **RabbitMQ** recibe los mensajes en la cola `logs_queue`

3. **Consumer** procesa cada mensaje:
   - Decodifica JSON
   - Valida datos
   - Inserta en tabla `logs`

4. **PostgreSQL** almacena los datos de forma persistente

---

## Mejoras Implementadas

**Healthchecks** en Docker Compose
**Logging estructurado** en Producer y Consumer
**Conexión persistente** a PostgreSQL (sin reconectar en cada mensaje)
**Validación de datos** en Producer
 **Reintentos automáticos** con backoff
**Mensajes persistentes** en RabbitMQ
**QoS (Quality of Service)** en Consumer
 **Manejo de errores** mejorado




