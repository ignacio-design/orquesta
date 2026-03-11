# Flujo de Leads: Telegram → HubSpot

## Cómo funciona

### 1️⃣ Bot califica lead en Telegram
El bot hace las 3 preguntas y obtiene:
- Nombre: Pato
- Empresa: Clínica Oftalmológica  
- Servicio: Automatización WhatsApp

### 2️⃣ Guardar el lead en `leads.json`

Después de calificar, ejecutá:

```bash
python3 << 'EOF'
import json

lead = {
    "nombre": "Pato",
    "apellido": "Carrere",
    "empresa": "Clínica Oftalmológica",
    "servicio": "Automatización WhatsApp"
}

# Leer leads existentes
try:
    with open("/Users/patocarrere/.openclaw/workspace/leads.json", "r") as f:
        leads = json.load(f)
except:
    leads = []

# Agregar el nuevo lead
leads.append(lead)

# Guardar
with open("/Users/patocarrere/.openclaw/workspace/leads.json", "w") as f:
    json.dump(leads, f, indent=2)

print("✅ Lead guardado en leads.json")
EOF
```

O más simple, directamente en bash:

```bash
cat > /Users/patocarrere/.openclaw/workspace/leads.json << 'EOF'
[
  {
    "nombre": "Pato",
    "apellido": "Carrere",
    "empresa": "Clínica Oftalmológica",
    "servicio": "Automatización WhatsApp"
  }
]
EOF
```

### 3️⃣ Cron job automático

**Cada minuto**, un cron job ejecuta:
```bash
python ~/.openclaw/workspace/process_leads.py
```

Esto:
- ✅ Lee `leads.json`
- ✅ Crea contacto en HubSpot
- ✅ Crea deal (negocio) en HubSpot
- ✅ Vincula contacto al deal
- ✅ Marca el lead como "processed"

### 4️⃣ Resultado en HubSpot

Aparece automáticamente:
- **Contacto:** Pato Carrere (Clínica Oftalmológica)
- **Deal:** "Clínica Oftalmológica - Automatización WhatsApp"
- **Etapa:** Nuevo (qualifiedtobuy)

---

## Archivos clave

- **`leads.json`** → Leads pendientes de procesar
- **`process_leads.py`** → Script que sincroniza con HubSpot
- **Cron job** → Ejecuta cada minuto automáticamente

## ✅ Integración Calendly

Cuando el bot termina de calificar un lead, ofrece el link de Calendly:

**Link:** https://calendly.com/ignacio-orquesta-ai/30min

El flujo final es:
1. Bot califica al lead (3 preguntas)
2. Bot ofrece agendar: "Podés agendar una reunión de 30 min aquí: https://calendly.com/ignacio-orquesta-ai/30min"
3. Lead agendado automáticamente
4. Datos guardados en HubSpot

## Próximas mejoras

- 🔄 Automatizar guardado de leads (sin pasos manuales)
- 🎯 Personalizar respuestas por rubro (oftalmología, e-commerce, etc.)
- 📊 Dashboard de leads en tiempo real
