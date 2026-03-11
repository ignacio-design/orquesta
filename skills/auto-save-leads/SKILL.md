# Auto Save Leads Skill

Automáticamente guarda leads completados en HubSpot sin intervención manual.

## Descripción

Cuando el bot de Orquesta termina de calificar un lead (después de las 3 preguntas), automáticamente:
1. Extrae los datos de la conversación
2. Guarda en leads.json
3. Cron job sincroniza a HubSpot

**Cero intervención manual.**

## Cómo Funciona

### El Flujo Automático

```
Usuario: "Hola, quiero automatizar procesos"
Bot: ¿A qué se dedica tu empresa?
Usuario: "Oftalmología"
Bot: ¿Qué querés automatizar?
Usuario: "Consultas por WhatsApp"
Bot: ¿Cuántos empleados?
Usuario: "4"
Bot: "Perfecto, agendá aquí: [link]"
✨ AUTOMÁTICO: Lead guardado en leads.json
⏰ 1 minuto después: Sincronizado a HubSpot
```

## Scripts Involucrados

- **`save_lead.py`** — Guarda un lead en leads.json
- **`auto_lead_webhook.py`** — Webhook listener de Telegram
- **`auto_lead_detector.py`** — Detector de conversaciones completadas
- **`auto_process_leads.py`** — Monitor que ejecuta cada minuto
- **`process_leads.py`** — Sincroniza a HubSpot (vía cron)

## Instalación

Los scripts ya están en `/Users/patocarrere/.openclaw/workspace/`

## Uso

**Automático** — No requiere acciones manuales

### Test Manual

```bash
python3 ~/.openclaw/workspace/auto_lead_webhook.py test
```

### Monitorear

```bash
tail -f ~/.openclaw/workspace/leads.json
```

## Configuración Cron

Ya está configurado en el gateway:

```
*/1 * * * * python ~/.openclaw/workspace/process_leads.py
```

Esto ejecuta cada minuto y sincroniza cualquier lead pendiente a HubSpot.

## Próximas Mejoras

- [ ] Integración con webhooks de Telegram en tiempo real
- [ ] Webhook de Calendly para actualizar etapa automáticamente
- [ ] Dashboard de monitoreo en vivo
- [ ] Alertas cuando se completa un lead

## Desarrollo

Para mejorar la auto-detección de leads, editar:
- `auto_lead_detector.py` — Regex patterns
- `telegram_webhook_handler.py` — Message processing

## Troubleshooting

### "No se guarda automáticamente"

Verificar que el cron está corriendo:
```bash
crontab -l
```

### "Datos incompletos"

Los patrones de detección necesitan ajustarse. Ver `extract_lead_data()` en los scripts.

## Docs Relacionadas

- `README.md` — Visión general
- `HUBSPOT_FLOW.md` — Flujo técnico
- `AUTOMATIZACION_LEADS.md` — Detalles de automatización
