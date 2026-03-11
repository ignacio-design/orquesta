#!/usr/bin/env python3
"""
Twilio WhatsApp Bot - Orquesta
Responde correctamente en TwiML
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
from datetime import datetime

# Files
LEADS_FILE = os.path.expanduser("~/.openclaw/workspace/leads.json")
CONVERSATIONS_FILE = os.path.expanduser("~/.openclaw/workspace/conversations.json")

app = Flask(__name__)

def log_msg(msg):
    """Log con timestamp"""
    ts = datetime.now().isoformat()
    print(f"[{ts}] {msg}")

def load_conversations():
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_conversations(data):
    with open(CONVERSATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_leads():
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_leads(leads):
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Webhook de Twilio - Responde en TwiML"""
    
    log_msg("📨 Webhook llamado")
    
    try:
        # Parsear mensaje
        incoming_msg = request.values.get('Body', '').strip()
        sender = request.values.get('From', '').replace('whatsapp:', '')
        
        log_msg(f"👤 De: {sender}")
        log_msg(f"💬 Mensaje: {incoming_msg[:100]}")
        
        # Crear respuesta TwiML
        resp = MessagingResponse()
        
        if not incoming_msg:
            resp.message("Hola 👋 ¿Cómo puedo ayudarte?")
            return str(resp)
        
        # Cargar conversaciones
        conversations = load_conversations()
        
        # Nueva conversación
        if sender not in conversations:
            log_msg(f"🆕 Nueva conversación de {sender}")
            conversations[sender] = {
                'step': 0,
                'data': {},
                'started_at': datetime.now().isoformat()
            }
            
            msg = "🎵 ¡Hola! Bienvenido a Orquesta.\n\nVamos a conocer tu negocio en 3 preguntas rápidas.\n\n¿Cuál es el nombre de tu empresa?"
            resp.message(msg)
            save_conversations(conversations)
            log_msg(f"✅ Respuesta enviada")
            return str(resp)
        
        conv = conversations[sender]
        step = conv['step']
        
        # Paso 1: Empresa
        if step == 0:
            conv['data']['empresa'] = incoming_msg
            conv['step'] = 1
            msg = "¡Perfecto! 📧\n\n¿Qué servicio de Orquesta te interesa?\n\n1️⃣ WhatsApp & CRM\n2️⃣ E-commerce Analytics\n3️⃣ Market Research"
            resp.message(msg)
            save_conversations(conversations)
            log_msg(f"✅ Paso 1: {incoming_msg}")
            return str(resp)
        
        # Paso 2: Servicio
        elif step == 1:
            servicios = {
                '1': 'WhatsApp & CRM',
                '2': 'E-commerce Analytics',
                '3': 'Market Research'
            }
            conv['data']['servicio'] = servicios.get(incoming_msg, incoming_msg)
            conv['step'] = 2
            msg = f"¡Excelente! Elegiste: {conv['data']['servicio']} ✨\n\n¿Cuántos empleados tiene tu empresa?"
            resp.message(msg)
            save_conversations(conversations)
            log_msg(f"✅ Paso 2: {conv['data']['servicio']}")
            return str(resp)
        
        # Paso 3: Empleados + GUARDAR
        elif step == 2:
            conv['data']['empleados'] = incoming_msg
            conv['step'] = 3
            
            # GUARDAR LEAD
            leads = load_leads()
            new_lead = {
                'id': len(leads) + 1,
                'nombre': conv['data'].get('empresa', 'N/A'),
                'empresa': conv['data'].get('empresa', 'N/A'),
                'servicio': conv['data'].get('servicio', 'N/A'),
                'empleados': conv['data'].get('empleados', 'N/A'),
                'whatsapp': sender,
                'status': 'nuevo',
                'fecha': datetime.now().isoformat(),
                'canal': 'WhatsApp'
            }
            leads.append(new_lead)
            save_leads(leads)
            
            log_msg(f"💾 Lead guardado: {new_lead['nombre']}")
            
            # Mensaje final
            final_msg = f"✅ ¡Listo! Recibimos tu información:\n\n📱 {conv['data']['empresa']}\n🎯 {conv['data']['servicio']}\n👥 {conv['data']['empleados']} empleados\n\nNuestro equipo te contactará en las próximas 24h.\n\n¿Preguntas? Escribe cuando quieras 💬"
            resp.message(final_msg)
            save_conversations(conversations)
            
            log_msg(f"✅ Lead completo")
            return str(resp)
        
        return str(resp)
        
    except Exception as e:
        log_msg(f"❌ Error: {e}")
        resp = MessagingResponse()
        resp.message("Error en el servidor. Intenta más tarde.")
        return str(resp)

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    log_msg("🚀 Twilio WhatsApp Bot iniciado")
    log_msg(f"🔗 Webhook: POST /webhook/whatsapp")
    log_msg(f"💾 Leads: {LEADS_FILE}")
    log_msg("Esperando mensajes...")
    app.run(host='0.0.0.0', port=5000, debug=False)
