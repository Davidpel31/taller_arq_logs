@echo off
REM Script de inicialización del sistema para Windows

setlocal enabledelayedexpansion

echo.
echo 🚀 Sistema de Logs - Inicializador
echo ===================================
echo.

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado
    pause
    exit /b 1
)

echo ✅ Docker está disponible
echo.

REM Menu
echo Selecciona una opción:
echo 1) Levantar sistema
echo 2) Levantar y reconstruir
echo 3) Ver logs (producer)
echo 4) Ver logs (consumer)
echo 5) Ver logs (postgres)
echo 6) Ver logs (rabbitmq)
echo 7) Conectarse a PostgreSQL
echo 8) Detener sistema
echo 9) Limpiar todo (elimina volúmenes)
echo.

set /p opcion="Opción (1-9): "

if "%opcion%"=="1" (
    echo 🔨 Levantando sistema...
    docker compose up -d
    echo ✅ Sistema levantado
    echo.
    echo 📍 RabbitMQ: http://localhost:15672 (guest/guest)
    echo 📊 PostgreSQL: localhost:5432 (postgres/postgres)
    echo.
    pause
) else if "%opcion%"=="2" (
    echo 🔨 Levantando sistema con rebuild...
    docker compose up --build -d
    echo ✅ Sistema levantado
    echo.
    pause
) else if "%opcion%"=="3" (
    echo 📤 Logs del Producer:
    docker logs -f producer
) else if "%opcion%"=="4" (
    echo 📥 Logs del Consumer:
    docker logs -f consumer
) else if "%opcion%"=="5" (
    echo 🐘 Logs de PostgreSQL:
    docker logs -f postgres
) else if "%opcion%"=="6" (
    echo 🐇 Logs de RabbitMQ:
    docker logs -f rabbitmq
) else if "%opcion%"=="7" (
    echo 🔓 Conectando a PostgreSQL...
    docker exec -it postgres psql -U postgres -d logsdb
) else if "%opcion%"=="8" (
    echo 🛑 Deteniendo sistema...
    docker compose down
    echo ✅ Sistema detenido
    echo.
    pause
) else if "%opcion%"=="9" (
    echo ⚠️  Esto eliminará TODOS los datos
    set /p confirmar="¿Estás seguro? (s/n): "
    if "!confirmar!"=="s" (
        echo 🧹 Limpiando...
        docker compose down -v
        echo ✅ Sistema limpiado
    ) else (
        echo ❌ Cancelado
    )
    echo.
    pause
) else (
    echo ❌ Opción inválida
    echo.
    pause
    exit /b 1
)
