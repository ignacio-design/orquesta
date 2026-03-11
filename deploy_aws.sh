#!/bin/bash
# Script de deploy para EC2

echo "🚀 ORQUESTA - SETUP EN AWS EC2"
echo "=============================="

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git

# Crear directorio
echo "📁 Creando directorio..."
mkdir -p ~/orquesta
cd ~/orquesta

# Crear virtual env
echo "🐍 Creando virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Clonar código (o copiar archivos)
echo "📥 Instalando dependencias..."
pip install requests psycopg2-binary python-dotenv

# Crear .env
echo "🔐 Creando archivo .env..."
cat > .env << EOF
# AWS RDS
DB_HOST=<TU_RDS_ENDPOINT>
DB_NAME=orquesta
DB_USER=postgres
DB_PASSWORD=<TU_PASSWORD>
DB_PORT=5432

# HubSpot
HUBSPOT_TOKEN=pat-na1-aa8b8d13-2e8a-407b-ae2e-df9e6963ac69
PORTAL_ID=51191100

# Calendly
CALENDLY_LINK=https://calendly.com/ignacio-orquesta-ai/30min
EOF

echo ""
echo "✅ CONFIGURACIÓN COMPLETA"
echo ""
echo "⚠️  PRÓXIMOS PASOS:"
echo "1. Edita .env con tu RDS endpoint y password"
echo "2. Copia los archivos HTML:"
echo "   - cp formulario.html ."
echo "   - cp dashboard.html ."
echo "   - cp app_production.py ."
echo "3. Inicia el servidor:"
echo "   python3 app_production.py"
echo ""
echo "4. (Opcional) Para ejecutar en background con supervisor:"
echo "   sudo apt-get install supervisor"
echo "   # Crea /etc/supervisor/conf.d/orquesta.conf"
echo ""
