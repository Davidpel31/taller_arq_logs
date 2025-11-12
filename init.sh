#!/bin/bash
# Script de inicialización del sistema

set -e

echo "🚀 Sistema de Logs - Inicializador"
echo "=================================="
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Verificar si Docker está corriendo
if ! docker ps &> /dev/null; then
    echo "❌ Docker no está corriendo. Inicia Docker Desktop."
    exit 1
fi

echo "✅ Docker está disponible"
echo ""

# Menu
echo "Selecciona una opción:"
echo "1) Levantar sistema (docker compose up -d)"
echo "2) Levantar y reconstruir (docker compose up --build -d)"
echo "3) Ver logs (producer)"
echo "4) Ver logs (consumer)"
echo "5) Ver logs (postgres)"
echo "6) Ver logs (rabbitmq)"
echo "7) Conectarse a PostgreSQL"
echo "8) Detener sistema"
echo "9) Limpiar todo (elimina volúmenes)"
echo ""

read -p "Opción (1-9): " opcion

case $opcion in
    1)
        echo "🔨 Levantando sistema..."
        docker compose up -d
        echo "✅ Sistema levantado"
        echo ""
        echo "📍 RabbitMQ: http://localhost:15672 (guest/guest)"
        echo "📊 PostgreSQL: localhost:5432 (postgres/postgres)"
        ;;
    2)
        echo "🔨 Levantando sistema con rebuild..."
        docker compose up --build -d
        echo "✅ Sistema levantado"
        ;;
    3)
        echo "📤 Logs del Producer:"
        docker logs -f producer
        ;;
    4)
        echo "📥 Logs del Consumer:"
        docker logs -f consumer
        ;;
    5)
        echo "🐘 Logs de PostgreSQL:"
        docker logs -f postgres
        ;;
    6)
        echo "🐇 Logs de RabbitMQ:"
        docker logs -f rabbitmq
        ;;
    7)
        echo "🔓 Conectando a PostgreSQL..."
        docker exec -it postgres psql -U postgres -d logsdb
        ;;
    8)
        echo "🛑 Deteniendo sistema..."
        docker compose down
        echo "✅ Sistema detenido"
        ;;
    9)
        echo "⚠️  Esto eliminará TODOS los datos"
        read -p "¿Estás seguro? (s/n): " confirmar
        if [ "$confirmar" = "s" ]; then
            echo "🧹 Limpiando..."
            docker compose down -v
            echo "✅ Sistema limpiado"
        else
            echo "❌ Cancelado"
        fi
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac
