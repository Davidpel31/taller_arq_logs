# 📊 Sistema de Logs con Arquitectura Productor-Consumidor

Un sistema distribuido para procesar y almacenar datos meteorológicos en tiempo real usando **RabbitMQ**, **PostgreSQL** y **Docker**.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────┐
│         Docker Compose Environment          │
├──────────────────┬──────────────┬───────────┤
│   PRODUCER       │   RABBITMQ   │  CONSUMER │
│   (Python)       │   (Broker)   │ (Python)  │
│   Genera datos   │   logs_queue │ Procesa   │
│   cada 5seg      │              │ e inserta │
└──────────┬───────┴────────┬─────┴───────┬───┘
           │                │             │
           └────────────────┴─────────────┘
                     │
                     ▼
              ┌─────────────┐
              │ PostgreSQL  │
              │   logsdb    │
              │   (logs)    │
              └─────────────┘
```

## 🎯 Características

- ✅ **Desacoplamiento**: Producer y Consumer independientes
- ✅ **Escalabilidad**: Múltiples consumers pueden procesadores
- ✅ **Persistencia**: Datos almacenados en PostgreSQL
- ✅ **Confiabilidad**: Reintentos automáticos y healthchecks
- ✅ **Logging**: Trazabilidad completa de operaciones
- ✅ **Validación**: Validación de datos antes de procesar

## 📋 Requisitos

- Docker Desktop 4.0+
- 2GB RAM disponible
- Puertos libres: 5432, 5672, 15672

## 🚀 Inicio Rápido

### 1. Levantar el sistema

```bash
docker compose up -d
```

### 2. Verificar servicios

```bash
docker ps
```

### 3. Acceder a RabbitMQ

```
http://localhost:15672
usuario: guest
contraseña: guest
```

### 4. Consultar datos en PostgreSQL

```bash
docker exec -it postgres psql -U postgres -d logsdb

# Ver datos
SELECT * FROM weather_logs ORDER BY id DESC LIMIT 10;
```

## 📁 Estructura del Proyecto

```
taller_arq_logs/
├── docker-compose.yml          # Orquestación de servicios
├── GUIA_USO.md                # Documentación detallada
├── README.md                  # Este archivo
├── .gitignore                 # Archivos a ignorar en Git
│
├── producer/
│   ├── producer.py            # Generador de datos
│   ├── Dockerfile             # Imagen Docker
│   └── requirements.txt        # Dependencias Python
│
├── consumer/
│   ├── consumer.py            # Procesador de datos
│   ├── Dockerfile             # Imagen Docker
│   └── requirements.txt        # Dependencias Python
│
└── db/
    ├── init.sql               # Script de inicialización
    └── init-scripts/          # Scripts adicionales SQL
        ├── 01-create-tables.sql
        └── 02-insert-data.sql
```

## 🔄 Flujo de Datos

1. **Producer**: Genera datos meteorológicos cada 5 segundos
   - Estación (1-5)
   - Temperatura (15-35°C)
   - Humedad (40-90%)
   - Timestamp

2. **RabbitMQ**: Encola los mensajes JSON

3. **Consumer**: Procesa y valida mensajes

4. **PostgreSQL**: Almacena en tabla `weather_logs`

## 🛠️ Mejoras Implementadas

### Consumer
- ✅ Conexión persistente (no reconecta cada mensaje)
- ✅ Logging estructurado
- ✅ Manejo de errores mejorado
- ✅ QoS configurado (prefetch_count=1)
- ✅ Validación de datos completos

### Producer
- ✅ Validación de datos antes de enviar
- ✅ Mensajes persistentes en RabbitMQ
- ✅ Logging de todas las operaciones
- ✅ Reintentos automáticos
- ✅ Eliminada dependencia innecesaria de PostgreSQL

### Infraestructura
- ✅ Healthchecks en PostgreSQL y RabbitMQ
- ✅ Reintentos automáticos (on-failure:5)
- ✅ Imagen Alpine para RabbitMQ (más ligera)
- ✅ Depends_on con condiciones de salud

## 📊 Consultas SQL Útiles

### Últimos registros
```sql
SELECT * FROM weather_logs ORDER BY id DESC LIMIT 10;
```

### Datos por estación
```sql
SELECT 
    estacion_id,
    COUNT(*) as registros,
    AVG(temperatura) as temp_promedio,
    MIN(temperatura) as temp_min,
    MAX(temperatura) as temp_max,
    AVG(humedad) as humedad_promedio
FROM weather_logs
GROUP BY estacion_id
ORDER BY estacion_id;
```

### Datos en rango de tiempo
```sql
SELECT * FROM weather_logs 
WHERE fecha BETWEEN NOW() - INTERVAL '1 hour' AND NOW()
ORDER BY fecha DESC;
```

## 🐛 Troubleshooting

### Los contenedores no inician
```bash
docker compose logs -f
```

### Resetear todo
```bash
docker compose down -v
docker compose up --build -d
```

### Ver logs de cada servicio
```bash
docker logs -f producer
docker logs -f consumer
docker logs -f postgres
docker logs -f rabbitmq
```

## 🔗 Puertos y Accesos

| Servicio | Puerto | Acceso |
|----------|--------|--------|
| PostgreSQL | 5432 | localhost:5432 |
| RabbitMQ AMQP | 5672 | localhost:5672 |
| RabbitMQ Web | 15672 | http://localhost:15672 |

## 📝 Credenciales por Defecto

| Servicio | Usuario | Contraseña |
|----------|---------|-----------|
| PostgreSQL | postgres | postgres |
| RabbitMQ | guest | guest |

## 🚦 Estado de Salud

Los servicios incluyen healthchecks automáticos:

```bash
# Ver estado de salud
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## 📚 Recursos Adicionales

- [RabbitMQ Docs](https://www.rabbitmq.com/documentation.html)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [pika (Python RabbitMQ)](https://pika.readthedocs.io/)

## 📄 Licencia

Este proyecto es de código abierto.

## ✉️ Autor

**David Pelaez** - [GitHub](https://github.com/Davidpel31)
