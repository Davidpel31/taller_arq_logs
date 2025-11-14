# Sistema de Logs con Arquitectura Productor-Consumidor

Un sistema distribuido para procesar y almacenar datos meteorológicos en tiempo real usando **RabbitMQ**, **PostgreSQL** y **Docker**.

## Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                      Docker Compose Stack                     │
├──────────────────────┬──────────────────────┬─────────────────┤
│      PRODUCER        │      RABBITMQ        │    CONSUMER     │
│    (Python + Pika)   │   (Broker AMQP)      │ (3 módulos)     │
│  Genera datos        │  Exchange: weather   │                 │
│  cada 5 segundos     │  Queue: logs_queue   │                 │
└─────────────┬────────┴───────────┬──────────┴───────────────┘
              │                    │
              └────────────────────┘
                       │
                       ▼
              ┌──────────────────────┐
              │     PostgreSQL       │
              │      logsdb          │
              │  Tabla: weather_logs │
              └──────────────────────┘

```
## Arquitectura del Consumer 

´´´sql
consumer/
│
├── consumer_validacion.py   
├── consumer_bd.py           
└── consumer_main.py         
´´´

**Resumen de Métricas de Rendimiento del Sistema**

El sistema Productor–Consumidor incluye métricas que permiten evaluar la velocidad, estabilidad y calidad del flujo de datos desde el Producer hasta PostgreSQL. Estas métricas ayudan a monitorear en tiempo real el comportamiento del sistema y detectar fallos.

1. **Métricas del Producer**

El Producer envía datos meteorológicos a RabbitMQ y genera las siguientes métricas:

**Mensajes enviados**

Cantidad total de mensajes publicados correctamente.

**Tiempo de publicación**

Tiempo que tarda en enviar un mensaje al broker.

**Velocidad (msg/s)**

Mensajes enviados por segundo, calculados cada 30 segundos.

**Errores de validación**

Cuando los datos aleatorios quedan fuera de los rangos establecidos, el Producer los descarta y registra el error.

2. **Métricas del Consumer**

El Consumer está separado en tres componentes: validación, base de datos y procesamiento principal. El módulo principal (consumer_main.py) genera métricas cada 30 segundos:

**messages_received**

Número total de mensajes recibidos desde RabbitMQ.

 **db_ok**

Inserciones exitosas en PostgreSQL.

 **db_errors**

Errores al guardar datos (cuando la BD falla o recibe información incorrecta).

**json_errors**

Errores al decodificar o validar JSON.

**msg/s**

Velocidad real del Consumer procesando mensajes.

**tiempo_promedio_proc**

Tiempo promedio de procesamiento por mensaje: validación + inserción + ACK.


**Características Principales**

**- Consumer dividido**

consumer_main.py → consume mensajes y controla el flujo

consumer_validacion.py → valida JSON

consumer_bd.py → conecta e inserta en PostgreSQL

- Mensajería confiable con RabbitMQ

- Persistencia real en PostgreSQL

- Todo orquestado con Docker

- Métricas de rendimiento en Producer y Consumer

- Reintentos automáticos + Healthchecks

- Sistema completamente validado

## Requisitos

- Docker Desktop 4.0+
- 2GB RAM disponible
- Puertos libres: 5432, 5672, 15672

**Cómo ejecutar el sistema**

**1. Detener y limpiar todo**
docker compose down -v

**2. Reconstruir el sistema COMPLETO**
docker compose up --build -d

**3. Verificar que todo está corriendo**
docker ps

**4. Ver logs del consumer**
docker compose logs -f consumer




**Acceder a RabbitMQ**
http://localhost:15672
usuario: guest
contraseña: guest


Podrás ver:

- Cola: logs_queue

- DLX: weather.dlx

- Cola secundaria: logs_dlx

- Tasa de mensajes (msg/s)

- Consumers activos

**Consultar datos en PostgreSQL**
docker exec -it postgres psql -U postgres -d logsdb


**Ejemplo:**
´´´sql

SELECT * FROM weather_logs ORDER BY id DESC LIMIT 10;
´´´

## Estructura del Proyecto

```
taller_arq_logs/
├── docker-compose.yml
├── README.md
│
├── producer/
│   ├── producer.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── consumer/
│   ├── consumer_validacion.py
│   ├── consumer_bd.py
│   ├── consumer_main.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── db/
    ├── init.sql
    └── migrations/

```

## Flujo de Datos

**Producer**

- Envía mensajes cada 5 segundos

- Datos meteorológicos simulados

**RabbitMQ**

- Recibe, enruta y almacena temporalmente mensajes

- DLX para mensajes inválidos

**Consumer**

- **consumer_validacion.py** → valida JSON y rangos

- **consumer_bd.py**→ inserta en PostgreSQL

- **consumer_main.py** → métricas + ACK manual

**PostgreSQL**

- Guarda datos en la tabla weather_logs

##  Mejoras Implementadas

### Consumer
- Conexión persistente (no reconecta cada mensaje)
- Logging estructurado
- Manejo de errores mejorado
- QoS configurado (prefetch_count=1)
- Validación de datos completos

### Producer
- Validación de datos antes de enviar
- Mensajes persistentes en RabbitMQ
- Logging de todas las operaciones
- Reintentos automáticos
- Eliminada dependencia innecesaria de PostgreSQL

### Infraestructura
- Healthchecks en PostgreSQL y RabbitMQ
- Reintentos automáticos (on-failure:5)
- Imagen Alpine para RabbitMQ (más ligera)
- Depends_on con condiciones de salud

## Consultas SQL Útiles

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



## Puertos y Accesos

| Servicio | Puerto | Acceso |
|----------|--------|--------|
| PostgreSQL | 5432 | localhost:5432 |
| RabbitMQ AMQP | 5672 | localhost:5672 |
| RabbitMQ Web | 15672 | http://localhost:15672 |

## Credenciales por Defecto

| Servicio | Usuario | Contraseña |
|----------|---------|-----------|
| PostgreSQL | postgres | postgres |
| RabbitMQ | guest | guest |

## Estado de Salud

Los servicios incluyen healthchecks automáticos:

```bash

docker ps --format "table {{.Names}}\t{{.Status}}"
```

## Recursos Adicionales

- [RabbitMQ Docs](https://www.rabbitmq.com/documentation.html)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [pika (Python RabbitMQ)](https://pika.readthedocs.io/)

## Licencia

Este proyecto es de código abierto.

## Autor

**David Pelaez** - [GitHub](https://github.com/Davidpel31)
