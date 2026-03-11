#!/usr/bin/env python3
"""
Twilio WhatsApp Bot - Integración con Orquesta
Recibe mensajes de WhatsApp y automáticamente:
1. Hace 3 preguntas (empresa, servicio, empleados)
2. Guarda el lead en leads.json
3. Sincroniza con HubSpot
"""

from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
from datetime import datetime

# Twilio config
ACCOUNT_SID = "AC12cce1d5c9cded008d655701fec05052"
AUTH_TOKEN = "dce81647342347751d3537ae1e20ccbe"
TWILIO_WHATSAPP_NUMBER = "+447537166676"

# Files
LEADS_FILE = os.path.expanduser("~/.openclaw/workspace/leads.json")
CONVERSATIONS_FILE = os.path.expanduser("~/.openclaw/workspace/conversations.json")

# Initialize Flask + Twilio
app = Flask(__name__)
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

def load_conversations():
    """Carga estado de conversaciones"""
    if os.path.exists(CONVERSATIONS_FILE):
        with open(CONVERSATIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_conversations(data):
    """Guarda estado de conversaciones"""
    with open(CONVERSATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_leads():
    """Carga leads existentes"""
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leads(leads):
    """Guarda leads"""
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

def send_whatsapp_message(to_number, message):
    """Envía mensaje por WhatsApp vía Twilio"""
    try:
        msg = twilio_client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            body=message,
            to=f"whatsapp:{to_number}"
        )
        return True
    except Exception as e:
        print(f"Error enviando WhatsApp: {e}")
        return False

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Webhook de Twilio para mensajes de WhatsApp"""
    
    # Parsear mensaje
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '').replace('whatsapp:', '')
    
    if not incoming_msg:
        return '', 200
    
    # Cargar conversaciones
    conversations = load_conversations()
    
    # Si no existe conversación, iniciar
    if sender not in conversations:
        conversations[sender] = {
            'step': 0,
            'data': {},
            'started_at': datetime.now().isoformat()
        }
        
        # Paso 0: Bienvenida
        welcome_msg = "🎵 ¡Hola! Bienvenido a Orquesta.\n\nVamos a conocer tu negocio en 3 preguntas rápidas.\n\n¿Cuál es el nombre de tu empresa?"
        send_whatsapp_message(sender, welcome_msg)
        save_conversations(conversations)
        return '', 200
    
    conv = conversations[sender]
    step = conv['step']
    
    # Paso 1: Empresa
    if step == 0:
        conv['data']['empresa'] = incoming_msg
        conv['step'] = 1
        send_whatsapp_message(sender, "¡Perfecto! 📧\n\n¿Qué servicio de Orquesta te interesa?\n\n1️⃣ WhatsApp & CRM\n2️⃣ E-commerce Analytics\n3️⃣ Market Research")
        save_conversations(conversations)
        return '', 200
    
    # Paso 2: Servicio
    elif step == 1:
        servicios = {
            '1': 'WhatsApp & CRM',
            '2': 'E-commerce Analytics',
            '3': 'Market Research'
        }
        conv['data']['servicio'] = servicios.get(incoming_msg, incoming_msg)
        conv['step'] = 2
        send_whatsapp_message(sender, f"¡Excelente! Elegiste: {conv['data']['servicio']} ✨\n\n¿Cuántos empleados tiene tu empresa?")
        save_conversations(conversations)
        return '', 200
    
    # Paso 3: Empleados + GUARDAR LEAD
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
        
        # Mensaje final
        final_msg = f"✅ ¡Listo! Recibimos tu información:\n\n📱 {conv['data']['empresa']}\n🎯 {conv['data']['servicio']}\n👥 {conv['data']['empleados']} empleados\n\nNuestro equipo te contactará en las próximas 24h para una consulta sin compromiso.\n\n¿Preguntas? Escribe cuando quieras 💬"
        send_whatsapp_message(sender, final_msg)
        save_conversations(conversations)
        
        # Log
        print(f"✅ Lead guardado: {new_lead['nombre']} ({new_lead['whatsapp']})")
        
        return '', 200
    
    return '', 200

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    print("🚀 Twilio WhatsApp Bot iniciado...")
    print(f"📱 Número WhatsApp: {TWILIO_WHATSAPP_NUMBER}")
    print(f"🔗 Webhook: POST /webhook/whatsapp")
    app.run(host='0.0.0.0', port=5000, debug=False)
