# HubSpot Sync Skill

Sincroniza leads calificados con HubSpot automáticamente.

## Descripción

Cuando el bot de Orquesta termina de calificar un lead (después de las 3 preguntas), guarda automáticamente la información en HubSpot como un contacto y un deal.

## Uso

Cuando hayas calificado a un lead con nombre, empresa y servicio, ejecuta:

```bash
python ~/.openclaw/workspace/process_leads.py
```

## Variables

- **PORTAL_ID:** 51191100
- **TOKEN:** pat-na1-aa8b8d13-2e8a-407b-ae2e-df9e6963ac69
- **LEADS_FILE:** ~/.openclaw/workspace/leads.json

## El flujo

1. **Bot califica un lead** en Telegram con:
   - Nombre
   - Empresa
   - Servicio de interés

2. **Usuario/bot guarda en leads.json**:
   ```json
   [
     {
       "nombre": "Pato",
       "apellido": "Carrere",
       "empresa": "Clínica Oftalmológica",
       "servicio": "Automatización WhatsApp"
     }
   ]
   ```

3. **Script procesa**:
   ```bash
   python ~/.openclaw/workspace/process_leads.py
   ```

4. **HubSpot se actualiza**:
   - ✅ Contacto creado
   - ✅ Deal creado
   - ✅ Vinculados entre sí

## Cron automático

Para ejecutar cada minuto:

```bash
cron add \
  --name "Process HubSpot Leads" \
  --schedule "*/1 * * * *" \
  --command "python ~/.openclaw/workspace/process_leads.py"
```

## Archivos relacionados

- `process_leads.py` — Script que procesa leads
- `leads.json` — Archivo donde se guardan los leads pendientes
- `hubspot_helper.py` — Funciones auxiliares de HubSpot
