# 🔗 CONFIGURACIÓN TWILIO WHATSAPP

## ¿QUÉ ACABAMOS DE CREAR?

Un bot de WhatsApp que:
1. ✅ Recibe mensajes en +447537166676
2. ✅ Hace 3 preguntas automáticas (empresa, servicio, empleados)
3. ✅ Guarda el lead en `leads.json`
4. ✅ Sincroniza con HubSpot cada minuto

## PASO 1: INICIAR LOS SERVICIOS

```bash
~/.openclaw/workspace/start_all.sh
```

Esto inicia:
- ✅ Telegram Bot
- ✅ WhatsApp Bot (puerto 5000)
- ✅ Form Server (puerto 8000)
- ✅ HubSpot Sync (cada minuto)
- ✅ Serveo tunnels (públicos)

## PASO 2: CONFIGURAR TWILIO WEBHOOK

### En Twilio Console:

1. **Ve a:** https://console.twilio.com/
2. **Sección:** Messaging → Settings → WhatsApp Business Account
3. **Busca:** WhatsApp Sandbox
4. **URL de Webhook:** Pega esto en "When a message comes in":

```
https://whatsapp-orquesta.serveo.net:5000/webhook/whatsapp
```

5. **Método:** POST
6. **Guardar**

### En Twilio CLI (alternativa):

```bash
twilio phone-numbers:list
twilio phone-numbers:update +447537166676 --sms-url https://whatsapp-orquesta.serveo.net:5000/webhook/whatsapp
```

## PASO 3: VERIFICAR QUE FUNCIONA

### Opción A: Desde tu teléfono
1. Agrega +447537166676 a tus contactos
2. Envía mensaje por WhatsApp: "Hola"
3. El bot responde: "🎵 ¡Hola! Bienvenido..."

### Opción B: Ver logs
```bash
tail -f /tmp/whatsapp.log
tail -f ~/.openclaw/workspace/leads.json
```

## FLUJO COMPLETO

```
📱 Cliente mensajea +447537166676 por WhatsApp
        ↓
🤖 Bot recibe en webhook (serveo tunnel)
        ↓
❓ Bot: "¿Cuál es el nombre de tu empresa?"
        ↓
💬 Cliente: "Mi Empresa SRL"
        ↓
❓ Bot: "¿Qué servicio te interesa?"
        ↓
💬 Cliente: "1 (WhatsApp & CRM)"
        ↓
❓ Bot: "¿Cuántos empleados tienes?"
        ↓
💬 Cliente: "15"
        ↓
✅ Lead guardado en leads.json
        ↓
🔄 Cron sync (cada minuto) → HubSpot contacto + deal
        ↓
📧 Email automático: "Nuevo lead: Mi Empresa SRL"
```

## ARCHIVOS CREADOS

```
~/.openclaw/workspace/
├── twilio_whatsapp_bot.py          # ← Bot WhatsApp
├── start_all.sh                    # ← Script maestro
├── telegram_bot_final.py           # ← Bot Telegram
├── form_server.py                  # ← Servidor formulario
├── process_leads.py                # ← Sincronización HubSpot
├── leads.json                      # ← Base de datos de leads
└── conversations.json              # ← Estado de conversaciones
```

## VARIABLES ALMACENADAS

**En `twilio_whatsapp_bot.py`:**
- `ACCOUNT_SID`: AC12cce1d5c9cded008d655701fec05052
- `AUTH_TOKEN`: dce81647342347751d3537ae1e20ccbe
- `TWILIO_WHATSAPP_NUMBER`: +447537166676

## TROUBLESHOOTING

### El bot no responde
```bash
# 1. Verificar que está corriendo
ps aux | grep twilio_whatsapp_bot.py

# 2. Ver logs
tail -f /tmp/whatsapp.log

# 3. Verificar webhook URL en Twilio Console
```

### Leads no aparecen en HubSpot
```bash
# 1. Verificar que leads.json tiene datos
cat ~/.openclaw/workspace/leads.json

# 2. Ejecutar sync manualmente
python3 ~/.openclaw/workspace/process_leads.py

# 3. Ver logs de sync
tail -f /tmp/sync.log
```

### Serveo tunnel caído
```bash
# Reiniciar
pkill -f serveo
~/.openclaw/workspace/start_all.sh
```

## COMANDOS ÚTILES

```bash
# Ver todos los procesos activos
ps aux | grep -E "telegram|twilio|form_server|process_leads"

# Ver último lead guardado
tail -5 ~/.openclaw/workspace/leads.json

# Ver conversaciones activas
cat ~/.openclaw/workspace/conversations.json | python3 -m json.tool

# Logs en tiempo real
tail -f /tmp/whatsapp.log /tmp/telegram.log /tmp/form.log

# Detener todo
pkill -f "telegram_bot_final.py"
pkill -f "twilio_whatsapp_bot.py"
pkill -f "form_server.py"
pkill -f "serveo"
```

## SEGURIDAD

⚠️ **IMPORTANTE:**
- Los tokens de Twilio NO deben estar en el código en producción
- Usa variables de entorno:

```bash
export TWILIO_ACCOUNT_SID="AC12cce1d5c9cded008d655701fec05052"
export TWILIO_AUTH_TOKEN="dce81647342347751d3537ae1e20ccbe"
```

Luego modifica `twilio_whatsapp_bot.py`:
```python
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
```

## PRÓXIMOS PASOS

✅ **Hecho:**
- WhatsApp Bot automático
- Guardado de leads
- Sincronización con HubSpot

⏳ **Próximo:**
- Configurar Stripe/MercadoPago para pagos
- Agregar más canales (SMS, etc)
- Dashboard avanzado con reportes
- Integraciones personalizadas

---

**Cualquier duda:** hola@orquesta.ai | +44 7537 166676
