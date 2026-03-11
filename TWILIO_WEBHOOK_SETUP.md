# Configurar Webhook de Twilio/WhatsApp - Paso a Paso

## ¿Qué estamos haciendo?

Cuando alguien te escribe en WhatsApp, Twilio nos lo va a enviar a nuestro servidor. Nosotros vamos a:
1. Recibir el mensaje
2. Detectar si completó las 3 preguntas
3. Guardar el lead **automáticamente**

---

## 📋 Requisitos

- [ ] Python 3 instalado
- [ ] `save_lead.py` en el workspace
- [ ] `twilio_webhook_handler.py` (acabamos de crear)
- [ ] **ngrok** (para exponer tu computadora a Internet)

---

## PASO 1️⃣: Instalar ngrok (solo una vez)

ngrok es una herramienta que expone tu computadora a Internet. Es como un "tunel" hacia tu máquina local.

### En Mac:
```bash
brew install ngrok
```

### En Linux:
```bash
# Descargar
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip

# Descomprimir
unzip ngrok-stable-linux-amd64.zip

# Mover a /usr/local/bin
sudo mv ngrok /usr/local/bin
```

### Verificar:
```bash
ngrok --version
```

---

## PASO 2️⃣: Iniciar el webhook (Terminal 1)

Abre una terminal y ejecuta:

```bash
cd ~/.openclaw/workspace

python3 twilio_webhook_handler.py
```

Deberías ver algo como:
```
============================================================
🔗 WEBHOOK DE TWILIO/WHATSAPP ACTIVO
============================================================
   Puerto: 8001
   URL pública: http://TU_IP:8001/twilio-webhook
   (Necesitás exponer esto con ngrok o similar)

📋 Esperando mensajes de WhatsApp...
============================================================
```

✅ **Deja esta terminal abierta todo el tiempo.**

---

## PASO 3️⃣: Exponer con ngrok (Terminal 2)

Abre **otra terminal** y ejecuta:

```bash
ngrok http 8001
```

Deberías ver algo como:
```
ngrok by @inconshrevable                                        (Ctrl+C to quit)

Session Status                online                                            
Account                       [tu email]
Version                        3.0.7
Region                         us (United States)
Latency                        43ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8001
```

**Lo importante:** copia esta URL:
```
https://xxxx-xxxx-xxxx.ngrok-free.app
```

✅ **Deja esta terminal abierta también.**

---

## PASO 4️⃣: Configurar en Twilio

Ahora vamos a decirle a Twilio dónde enviarnos los mensajes.

### A. Ve a Twilio Console
https://console.twilio.com/

### B. Selecciona tu proyecto Orquesta

### C. Ve a Messaging → WhatsApp → Sandbox

O si lo tienes en producción:
Messaging → WhatsApp → Senders

### D. Busca "When a message comes in" o "Webhook URL"

Encontrarás una sección que dice algo como:
```
When a message comes in POST to:
[_________________]
```

### E. Ingresa tu URL pública

Copia la URL de ngrok + `/twilio-webhook`:

```
https://xxxx-xxxx-xxxx.ngrok-free.app/twilio-webhook
```

Selecciona: **POST** (no GET)

### F. GUARDA

Botón "Save"

---

## 🧪 PASO 5️⃣: Prueba

Ahora prueba enviando un mensaje a tu número de WhatsApp:

```
Envía esto:

Hola, quiero automatizar
→ El bot pregunta: ¿A qué se dedica tu empresa?

Farmacia
→ El bot pregunta: ¿Qué querés automatizar?

Consultas por WhatsApp
→ El bot pregunta: ¿Cuántos empleados?

5
→ ✅ El bot dice "Perfecto! Agendá aquí: [link]"
```

### Verificar que guardó:

En la **Terminal 1** (webhook), deberías ver:

```
📩 Mensaje de whatsapp:+34612345678: Farmacia
   Mensajes en conversación: 2
   Extrayendo datos... empresa=None, servicio=None
   ✓ Empresa detectada: Farmacia
   📊 Estado: empresa✓ servicio✗ empleados✗

📩 Mensaje de whatsapp:+34612345678: Consultas por WhatsApp
   Mensajes en conversación: 3
   ✓ Servicio detectado: Consultas Por Whatsapp
   📊 Estado: empresa✓ servicio✓ empleados✗

📩 Mensaje de whatsapp:+34612345678: 5
   Mensajes en conversación: 4
   ✓ Empleados detectados: 5
   📊 Estado: empresa✓ servicio✓ empleados✓ → COMPLETO
   💾 Guardando: Prospecto de Farmacia
   ✅ Lead guardado exitosamente
```

### Verificar que está en leads.json:

```bash
cat ~/.openclaw/workspace/leads.json
```

Deberías ver tu lead ahí:
```json
[
  {
    "nombre": "Prospecto",
    "apellido": "WhatsApp",
    "empresa": "Farmacia",
    "servicio": "Consultas Por Whatsapp",
    "timestamp": "2026-03-11T10:25:00"
  }
]
```

---

## 🔄 PASO 6️⃣: Verificar que HubSpot se actualiza

Después de 1 minuto, ejecuta:

```bash
cat ~/.openclaw/workspace/process_leads.py
```

O simplemente revisa tu HubSpot:
- Dashboard
- Contacts
- Deberías ver el nuevo contacto "Prospecto"

---

## ⚠️ Posibles Problemas

### "ngrok: command not found"
→ Reinstala ngrok (PASO 1)

### "Error: port already in use"
→ Cambiar puerto:
```bash
python3 twilio_webhook_handler.py 8002
# Y luego en ngrok:
ngrok http 8002
```

### "No me llega el mensaje al webhook"
→ Verifica:
1. ¿Ngrok está corriendo? (vira la Terminal 2)
2. ¿La URL en Twilio es correcta?
3. ¿Es HTTPS? (ngrok proporciona HTTPS, úsala)
4. ¿Hiciste SAVE en Twilio?

### "No detecta la empresa/servicio"
→ Vira `twilio_webhook_handler.py` línea ~70, en `extract_lead_data()`
→ Podríamos agregar más patrones de regex

---

## 📊 Resumen

Ahora tenés:
```
Cliente escribe en WhatsApp
    ↓
Twilio → ngrok → twilio_webhook_handler.py
    ↓
Detecta empresa/servicio/empleados
    ↓
Si están los 3 → save_lead.py guarda automáticamente
    ↓
Cada minuto → process_leads.py sincroniza a HubSpot
    ↓
✅ DONE - Sin intervención manual
```

---

## 🎯 Próximos pasos

Una vez que esté funcionando, podemos:
1. **Agregar el nombre del cliente** (detectarlo del mensaje)
2. **Enviar respuesta automática** cuando se guarda
3. **Notificarte por email/Telegram** cuando se guarda un lead
4. **Hacer ngrok permanente** (sin que expire cada 2 horas)

---

## ❓ ¿Preguntas?

Pregunta sobre qué paso no entendés y te lo explico más.
