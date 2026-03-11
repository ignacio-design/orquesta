# 🚀 Orquesta Bot - Sistema Completo

**Estado:** Operativo ✅  
**Última actualización:** 10 de marzo, 2026

---

## 📱 Canales Activos

### Telegram
- **Bot:** @orquestai_bot
- **Status:** ✅ Activo
- **Funcionalidad:** Califica leads en 3 preguntas

### WhatsApp
- **Número:** +447537166676
- **Provider:** Twilio
- **Status:** ✅ Activo
- **Funcionalidad:** Idéntica a Telegram

---

## 🔄 El Flujo Completo

### 1️⃣ Cliente contacta el bot
```
Telegram: @orquestai_bot
WhatsApp: +447537166676
```

### 2️⃣ Bot presenta Orquesta
```
"Soy el asistente de Orquesta, agencia de IA..."
```

### 3️⃣ Bot hace 3 preguntas
- ¿A qué se dedica tu empresa?
- ¿Qué querés automatizar?
- ¿Cuántos empleados tienen?

### 4️⃣ Bot ofrece agendar
```
"Podés agendar aquí: https://calendly.com/ignacio-orquesta-ai/30min"
```

### 5️⃣ Tú ejecutás un comando
```bash
guardar_lead "Nombre" "Apellido" "Empresa" "Servicio"
```

### 6️⃣ Cron job sincroniza a HubSpot
- ✅ Contacto creado
- ✅ Deal abierto
- ✅ Etapa: "Nuevo" (qualifiedtobuy)

---

## 🛠️ Componentes

### Telegram Bot
- Token: `8689609607:AAEvfHhG6j83OwZM2F2EUOYTQK9QJygFsXE`
- Modelo: Claude Haiku (rápido y económico)
- Responde: ~1-2 segundos

### HubSpot CRM
- Portal ID: `51191100`
- Pipeline: Estándar (7 etapas)
- Sincronización: Automática cada minuto
- Datos: Contactos + Deals

### Calendly
- Link: https://calendly.com/ignacio-orquesta-ai/30min
- Duración: 30 minutos
- Sincronización: Manual (próximamente automática)

### Twilio WhatsApp
- Account SID: `AC12cce1d5c9cded008d655701fec05052`
- Número: `+447537166676`
- Modo: Polling (no webhooks)

---

## 📂 Archivos Importantes

| Archivo | Función |
|---------|---------|
| `save_lead.py` | Guarda un lead en leads.json |
| `guardar_lead.sh` | Bash script para guardar (alias) |
| `process_leads.py` | Sincroniza a HubSpot (cron job) |
| `leads.json` | Database de leads pendientes |
| `HUBSPOT_FLOW.md` | Documentación técnica |
| `AUTOMATIZACION_LEADS.md` | Cómo guardar leads |
| `MEMORY.md` | Estado del proyecto |

---

## ⚡ Comandos Útiles

### Guardar un lead
```bash
guardar_lead "Pato" "Carrere" "Clínica Oftalmológica" "WhatsApp"
```

### Ver leads pendientes
```bash
cat ~/.openclaw/workspace/leads.json
```

### Procesar leads manualmente
```bash
python ~/.openclaw/workspace/process_leads.py
```

### Ver estado del bot
```bash
openclaw channels status
```

### Ver logs
```bash
openclaw logs | tail -50
```

---

## 🔮 Próximos Pasos (Esta semana)

### Fase 2 — Automatización Total
- [ ] Webhook de Telegram (detecta fin de flujo)
- [ ] Guardado automático (sin intervención manual)
- [ ] Webhook de Calendly (actualiza HubSpot)

### Fase 3 — Monetización
- [ ] Integrar Stripe / MercadoPago
- [ ] Procesar pagos desde el bot
- [ ] Facturación automática

### Fase 4 — Escalabilidad
- [ ] Instagram DM
- [ ] Facebook Messenger
- [ ] Web chat

---

## 💡 Consejos de Uso

1. **Para cada lead:** Ejecutá `guardar_lead` con los datos
2. **HubSpot procesará automáticamente** cada minuto
3. **Los datos son seguros:** Guardados localmente en leads.json
4. **Escalable:** Puede manejar +100 leads/día sin problema

---

## 📞 Contacto

- **Email:** ignacio@orquesta-ai.com
- **Web:** orquestaai.com
- **Telegram:** @orquestai_bot
- **WhatsApp:** +447537166676

---

**¡Sistema listo para capturar y procesar leads! 🚀**
