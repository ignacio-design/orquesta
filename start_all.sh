#!/bin/bash

echo "🎵 ORQUESTA - Iniciando todos los servicios..."

WORKSPACE="$HOME/.openclaw/workspace"
cd "$WORKSPACE"

# Kill previous processes
pkill -f "telegram_bot_final.py"
pkill -f "twilio_whatsapp_bot.py"
pkill -f "form_server.py"
pkill -f "process_leads.py"
pkill -f "serveo"

sleep 1

# 1. Telegram Bot
echo "1️⃣ Iniciando Telegram Bot..."
python3 telegram_bot_final.py > /tmp/telegram.log 2>&1 &
TELEGRAM_PID=$!
echo "   ✅ Telegram Bot PID: $TELEGRAM_PID"

# 2. Twilio WhatsApp Bot
echo "2️⃣ Iniciando Twilio WhatsApp Bot..."
pip install -q flask twilio > /dev/null 2>&1
python3 twilio_whatsapp_bot.py > /tmp/whatsapp.log 2>&1 &
WHATSAPP_PID=$!
echo "   ✅ WhatsApp Bot PID: $WHATSAPP_PID"

# 3. Form Server
echo "3️⃣ Iniciando Form Server (puerto 8000)..."
python3 form_server.py > /tmp/form.log 2>&1 &
FORM_PID=$!
echo "   ✅ Form Server PID: $FORM_PID"

# 4. Cron Sync (cada minuto)
echo "4️⃣ Iniciando Cron Sync HubSpot..."
while true; do
    python3 process_leads.py > /tmp/sync.log 2>&1
    sleep 60
done &
SYNC_PID=$!
echo "   ✅ Cron Sync PID: $SYNC_PID"

# 5. Serveo tunnel para WhatsApp Webhook
echo "5️⃣ Iniciando Serveo tunnel para Twilio..."
ssh -R whatsapp-orquesta:5000:localhost:5000 serveo.net > /tmp/serveo-whatsapp.log 2>&1 &
SERVEO_WHATSAPP_PID=$!
echo "   ✅ Serveo (WhatsApp) PID: $SERVEO_WHATSAPP_PID"

# 6. Serveo tunnel para Form
echo "6️⃣ Iniciando Serveo tunnel para Formulario..."
ssh -R form-orquesta:8000:localhost:8000 serveo.net > /tmp/serveo-form.log 2>&1 &
SERVEO_FORM_PID=$!
echo "   ✅ Serveo (Form) PID: $SERVEO_FORM_PID"

sleep 3

echo ""
echo "════════════════════════════════════════════════════"
echo "✅ ORQUESTA INICIADO CON ÉXITO"
echo "════════════════════════════════════════════════════"
echo ""
echo "📊 SERVICIOS ACTIVOS:"
echo "   1️⃣ Telegram Bot (@orquestai_bot)"
echo "   2️⃣ WhatsApp Bot (+447537166676)"
echo "   3️⃣ Form Server (http://localhost:8000)"
echo "   4️⃣ HubSpot Sync (cada minuto)"
echo ""
echo "🔗 URLS PÚBLICAS:"
echo "   📱 WhatsApp Webhook: https://whatsapp-orquesta.serveo.net:5000/webhook/whatsapp"
echo "   📋 Formulario: https://form-orquesta.serveo.net/"
echo "   📊 Dashboard: https://form-orquesta.serveo.net/dashboard"
echo ""
echo "💾 ARCHIVOS:"
echo "   Leads: $WORKSPACE/leads.json"
echo "   Conversaciones: $WORKSPACE/conversations.json"
echo ""
echo "🛑 PARA DETENER TODO:"
echo "   pkill -f 'telegram_bot_final.py'"
echo "   pkill -f 'twilio_whatsapp_bot.py'"
echo "   pkill -f 'form_server.py'"
echo "   pkill -f 'serveo'"
echo ""
echo "📝 LOGS:"
echo "   tail -f /tmp/telegram.log"
echo "   tail -f /tmp/whatsapp.log"
echo "   tail -f /tmp/form.log"
echo "════════════════════════════════════════════════════"
