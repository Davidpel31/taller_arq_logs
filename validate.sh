#!/bin/bash
# Script de validación del proyecto
# Uso: bash validate.sh

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              VALIDACIÓN COMPLETA DEL PROYECTO                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Variables
ERRORS=0
WARNINGS=0
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para imprimir error
error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

# Función para imprimir advertencia
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 1. VALIDANDO ESTRUCTURA DE ARCHIVOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Archivos obligatorios
files_required=(
    "docker-compose.yml"
    "README.md"
    "GUIA_USO.md"
    "CAMBIOS.md"
    "producer/producer.py"
    "producer/Dockerfile"
    "producer/requirements.txt"
    "consumer/consumer.py"
    "consumer/Dockerfile"
    "consumer/requirements.txt"
    "db/init.sql"
)

for file in "${files_required[@]}"; do
    if [ -f "$file" ]; then
        success "Archivo encontrado: $file"
    else
        error "Archivo NO encontrado: $file"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 2. VALIDANDO SINTAXIS PYTHON"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Validar sintaxis Python si python está disponible
if command -v python3 >/dev/null 2>&1; then
    if python3 -m py_compile producer/producer.py 2>/dev/null; then
        success "Sintaxis válida: producer/producer.py"
    else
        error "Sintaxis inválida: producer/producer.py"
    fi
    
    if python3 -m py_compile consumer/consumer.py 2>/dev/null; then
        success "Sintaxis válida: consumer/consumer.py"
    else
        error "Sintaxis inválida: consumer/consumer.py"
    fi
else
    warning "Python3 no disponible para validar sintaxis"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 3. VALIDANDO DOCKER COMPOSE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v docker >/dev/null 2>&1; then
    if docker compose config >/dev/null 2>&1; then
        success "Docker Compose válido"
    else
        error "Docker Compose NO válido"
    fi
else
    warning "Docker no está disponible"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 4. VALIDANDO ARCHIVOS DE CONFIGURACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar .gitignore
if [ -f ".gitignore" ]; then
    success ".gitignore presente"
else
    warning ".gitignore NO encontrado"
fi

# Verificar .env.example
if [ -f ".env.example" ]; then
    success ".env.example presente"
else
    warning ".env.example NO encontrado"
fi

# Verificar Makefile
if [ -f "Makefile" ]; then
    success "Makefile presente"
else
    warning "Makefile NO encontrado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 5. VALIDANDO DOCUMENTACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docs_required=(
    "README.md"
    "GUIA_USO.md"
    "CAMBIOS.md"
    "RESUMEN.md"
    "BEST_PRACTICES.md"
    "CONFIGURACION_AVANZADA.md"
)

for doc in "${docs_required[@]}"; do
    if [ -f "$doc" ]; then
        lines=$(wc -l < "$doc")
        success "Documento: $doc ($lines líneas)"
    else
        error "Documento NO encontrado: $doc"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 6. VALIDANDO TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "tests" ]; then
    success "Carpeta tests/ existe"
    test_files=$(find tests -name "*.py" -type f | wc -l)
    if [ "$test_files" -gt 0 ]; then
        success "Archivos de tests encontrados: $test_files"
    else
        warning "No hay archivos de tests"
    fi
else
    warning "Carpeta tests/ NO encontrada"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 7. VALIDANDO DEPENDENCIAS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar requirements.txt
if grep -q "pika" producer/requirements.txt && grep -q "psycopg2" producer/requirements.txt; then
    success "requirements.txt (producer) - Dependencias correctas"
else
    error "requirements.txt (producer) - Dependencias incompletas"
fi

if grep -q "pika" consumer/requirements.txt && grep -q "psycopg2" consumer/requirements.txt; then
    success "requirements.txt (consumer) - Dependencias correctas"
else
    error "requirements.txt (consumer) - Dependencias incompletas"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 8. VALIDANDO CONTENIDO CRÍTICO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Producer debe tener validación
if grep -q "def validar_datos" producer/producer.py; then
    success "producer.py - Función validar_datos presente"
else
    error "producer.py - Función validar_datos NO encontrada"
fi

# Producer debe tener logging
if grep -q "logger" producer/producer.py; then
    success "producer.py - Logging presente"
else
    error "producer.py - Logging NO encontrado"
fi

# Consumer debe tener pool de conexiones
if grep -q "db_connection" consumer/consumer.py; then
    success "consumer.py - Manejo de conexiones presente"
else
    error "consumer.py - Manejo de conexiones NO encontrado"
fi

# Consumer debe tener logging
if grep -q "logger" consumer/consumer.py; then
    success "consumer.py - Logging presente"
else
    error "consumer.py - Logging NO encontrado"
fi

# Docker-compose debe tener healthchecks
if grep -q "healthcheck:" docker-compose.yml; then
    success "docker-compose.yml - Healthchecks presente"
else
    error "docker-compose.yml - Healthchecks NO encontrado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 9. ESTADÍSTICAS DEL PROYECTO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Contar líneas de código
producer_lines=$(wc -l < producer/producer.py)
consumer_lines=$(wc -l < consumer/consumer.py)
total_code_lines=$((producer_lines + consumer_lines))

echo "📝 Líneas de código:"
echo "  • producer/producer.py: $producer_lines líneas"
echo "  • consumer/consumer.py: $consumer_lines líneas"
echo "  • Total: $total_code_lines líneas"

# Contar archivos
total_files=$(find . -type f -not -path './.git/*' | wc -l)
echo ""
echo "📁 Total de archivos: $total_files"

# Tamaño del proyecto
total_size=$(du -sh . | cut -f1)
echo "📦 Tamaño total: $total_size"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 RESUMEN DE VALIDACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ VALIDACIÓN EXITOSA - SIN ERRORES${NC}"
else
    echo -e "${RED}❌ VALIDACIÓN CON ERRORES: $ERRORS${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  ADVERTENCIAS: $WARNINGS${NC}"
fi

echo ""
echo "📋 Resumen:"
echo "  • Errores: $ERRORS"
echo "  • Advertencias: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✨ Proyecto validado correctamente${NC}"
    echo ""
    echo "🚀 Próximos pasos:"
    echo "  1. docker compose up -d"
    echo "  2. docker logs -f consumer"
    echo "  3. docker exec -it postgres psql -U postgres -d logsdb"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Por favor, corrija los errores antes de continuar${NC}"
    echo ""
    exit 1
fi
