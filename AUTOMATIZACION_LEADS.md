# Automatización de Guardado de Leads

## Problema actual
Cuando el bot califica un lead, los datos están en la conversación pero hay que guardarlos manualmente en `leads.json`.

## Solución: Guardar automáticamente

### Opción A — Comando Manual Simple (Hoy mismo)

Cuando el bot termina de calificar, simplemente ejecutá:

```bash
bash ~/.openclaw/workspace/guardar_lead.sh "Pato" "Carrere" "Clínica Oftalmológica" "Automatización WhatsApp"
```

O más simple, con un alias:

```bash
alias guardar_lead='bash ~/.openclaw/workspace/guardar_lead.sh'

# Luego:
guardar_lead "Pato" "Carrere" "Clínica Oftalmológica" "WhatsApp"
```

### Opción B — Automatización Total (Webhook)

**En desarrollo:** Un webhook que automáticamente guarda leads cuando:
1. El bot termina la secuencia de 3 preguntas
2. El usuario responde la última pregunta
3. El bot dice "Guardando tus datos..."

Esto se implementa con:
- Webhook de Telegram → Detecta fin de flujo
- Script ejecuta save_lead.py automáticamente
- **Usuario no hace nada extra**

---

## Flujo Actual (Semi-automático)

### 1️⃣ Usuario habla con bot en Telegram/WhatsApp

```
Usuario: Hola, quiero automatizar procesos
Bot: ¿A qué se dedica tu empresa?
Usuario: Oftalmología
Bot: ¿Qué querés automatizar?
Usuario: Consultas por WhatsApp
Bot: ¿Cuántos empleados?
Usuario: 4
Bot: Perfecto, agendá aquí: [link Calendly]
```

### 2️⃣ Tú ejecutás el comando (una línea)

```bash
guardar_lead "Pato" "Carrere" "Clínica Oftalmológica" "WhatsApp"
```

### 3️⃣ Cron job procesa cada minuto

```
✅ Contacto creado en HubSpot
✅ Deal creado
✅ Vinculados automáticamente
```

---

## Archivos

- `save_lead.py` — Guarda un lead en leads.json
- `guardar_lead.sh` — Alias bash para hacerlo más fácil
- `auto_capture_leads.py` — Helper para futura automatización
- `process_leads.py` — Procesa leads a HubSpot (cron job)

---

## Próximo: Automatización Total (Esta semana)

Una vez que tengamos los datos fluyendo bien, implementaremos:
- Webhook que detecte fin de flujo
- Script que guarde automáticamente
- **Cero intervención manual**
