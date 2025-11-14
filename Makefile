.PHONY: help build up down logs clean restart rebuild test install-deps

# Variables
COMPOSE := docker compose
PYTHON := python3
PIP := pip3

help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║                    COMANDOS DISPONIBLES                        ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 INICIO Y PARADA"
	@echo "  make up              Levantar todos los servicios"
	@echo "  make build           Construir imágenes Docker"
	@echo "  make rebuild         Reconstruir todo desde cero"
	@echo "  make down            Detener servicios"
	@echo "  make clean           Limpiar todo (incluyendo volúmenes)"
	@echo ""
	@echo "📊 MONITOREO"
	@echo "  make logs-all        Ver logs de todos los servicios"
	@echo "  make logs-producer   Ver logs del producer"
	@echo "  make logs-consumer   Ver logs del consumer"
	@echo "  make logs-postgres   Ver logs de PostgreSQL"
	@echo "  make logs-rabbitmq   Ver logs de RabbitMQ"
	@echo ""
	@echo "🔧 DESARROLLO"
	@echo "  make test            Ejecutar tests unitarios"
	@echo "  make install-deps    Instalar dependencias Python"
	@echo "  make lint            Verificar código con pylint (si está instalado)"
	@echo "  make format          Formatear código (si está instalado)"
	@echo ""
	@echo "💾 BASE DE DATOS"
	@echo "  make psql            Conectarse a PostgreSQL"
	@echo "  make psql-list       Listar datos en tabla logs"
	@echo "  make psql-count      Contar registros"
	@echo "  make psql-stats      Ver estadísticas por estación"
	@echo ""
	@echo "🐇 RABBITMQ"
	@echo "  make rabbitmq-ui     Acceder a RabbitMQ (http://localhost:15672)"
	@echo ""
	@echo "🏥 VERIFICACIÓN"
	@echo "  make status          Ver estado de contenedores"
	@echo "  make health          Ver healthchecks"
	@echo "  make info            Ver información del proyecto"
	@echo ""

# 🚀 INICIO Y PARADA
up:
	@echo "🚀 Levantando servicios..."
	$(COMPOSE) up -d
	@echo "✅ Servicios levantados"
	@echo ""
	@echo "📍 Accesos:"
	@echo "  RabbitMQ:   http://localhost:15672 (guest/guest)"
	@echo "  PostgreSQL: localhost:5432"

build:
	@echo "🔨 Construyendo imágenes..."
	$(COMPOSE) build

rebuild: down
	@echo "🔄 Reconstruyendo todo..."
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d
	@echo "✅ Reconstrucción completada"

down:
	@echo "🛑 Deteniendo servicios..."
	$(COMPOSE) down
	@echo "✅ Servicios detenidos"

clean: down
	@echo "🧹 Limpiando volúmenes..."
	$(COMPOSE) down -v
	@echo "✅ Limpieza completada"

restart: down up
	@echo "✅ Servicios reiniciados"

# 📊 MONITOREO
logs-all:
	@echo "📊 Logs de todos los servicios:"
	$(COMPOSE) logs -f

logs-producer:
	@echo "📤 Logs del Producer:"
	docker logs -f producer

logs-consumer:
	@echo "📥 Logs del Consumer:"
	docker logs -f consumer

logs-postgres:
	@echo "🐘 Logs de PostgreSQL:"
	docker logs -f postgres

logs-rabbitmq:
	@echo "🐇 Logs de RabbitMQ:"
	docker logs -f rabbitmq

# 🔧 DESARROLLO
test:
	@echo "🧪 Ejecutando tests..."
	@if command -v pytest >/dev/null; then \
		pytest tests/ -v; \
	else \
		echo "⚠️  pytest no está instalado. Ejecuta: pip install pytest"; \
	fi

install-deps:
	@echo "📦 Instalando dependencias..."
	$(PIP) install -r producer/requirements.txt
	$(PIP) install -r consumer/requirements.txt
	$(PIP) install pytest pylint black
	@echo "✅ Dependencias instaladas"

lint:
	@echo "🔍 Verificando código..."
	@if command -v pylint >/dev/null; then \
		pylint producer/producer.py consumer/consumer.py; \
	else \
		echo "⚠️  pylint no está instalado. Ejecuta: pip install pylint"; \
	fi

format:
	@echo "✨ Formateando código..."
	@if command -v black >/dev/null; then \
		black producer/producer.py consumer/consumer.py; \
	else \
		echo "⚠️  black no está instalado. Ejecuta: pip install black"; \
	fi

# 💾 BASE DE DATOS
psql:
	@echo "🔓 Conectando a PostgreSQL..."
	docker exec -it postgres psql -U postgres -d logsdb

psql-list:
	@echo "📋 Últimos 10 registros:"
	docker exec postgres psql -U postgres -d logsdb -c "SELECT * FROM weather_logs ORDER BY id DESC LIMIT 10;"

psql-count:
	@echo "📊 Total de registros:"
	docker exec postgres psql -U postgres -d logsdb -c "SELECT COUNT(*) as total FROM weather_logs;"

psql-stats:
	@echo "📈 Estadísticas por estación:"
	docker exec postgres psql -U postgres -d logsdb -c \
		"SELECT estacion_id, COUNT(*) as registros, AVG(temperatura) as temp_promedio, AVG(humedad) as humedad_promedio FROM weather_logs GROUP BY estacion_id ORDER BY estacion_id;"

# 🐇 RABBITMQ
rabbitmq-ui:
	@echo "🐇 Abriendo RabbitMQ Management UI..."
	@echo "   URL: http://localhost:15672"
	@echo "   Usuario: guest"
	@echo "   Contraseña: guest"
	@echo ""
	@echo "Presiona Ctrl+C para finalizar"
	@which xdg-open >/dev/null 2>&1 && xdg-open http://localhost:15672 || \
	which open >/dev/null 2>&1 && open http://localhost:15672 || \
	echo "⚠️  No se pudo abrir el navegador automáticamente"

# 🏥 VERIFICACIÓN
status:
	@echo "📊 Estado de contenedores:"
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.RunningFor}}"

health:
	@echo "🏥 Estado de salud:"
	@docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(postgres|rabbitmq|producer|consumer)" || echo "No hay contenedores en ejecución"

info:
	@echo "ℹ️  Información del Proyecto:"
	@echo ""
	@echo "📁 Nombre: taller_arq_logs"
	@echo "🏗️  Arquitectura: Productor-Consumidor con RabbitMQ"
	@echo "💾 Base de Datos: PostgreSQL 16"
	@echo "🐇 Message Broker: RabbitMQ 3"
	@echo "🐍 Lenguaje: Python 3.11"
	@echo ""
	@echo "📊 Servicios:"
	@echo "  • Producer: Generador de datos meteorológicos"
	@echo "  • Consumer: Procesador de datos"
	@echo "  • RabbitMQ: Broker de mensajes"
	@echo "  • PostgreSQL: Base de datos persistente"
	@echo ""
	@echo "📚 Documentación:"
	@echo "  • README.md: Documentación principal"
	@echo "  • GUIA_USO.md: Guía paso a paso"
	@echo "  • CAMBIOS.md: Cambios realizados"
	@echo "  • BEST_PRACTICES.md: Mejores prácticas"
	@echo ""

ps:
	@docker ps

# Alias útiles
start: up
stop: down
restart: restart
status: status
