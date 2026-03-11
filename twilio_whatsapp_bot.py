#!/usr/bin/env python3
"""
Twilio WhatsApp Bot - Orquesta
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
import tempfile
from datetime import datetime

# Use /tmp for Render compatibility
TEMP_DIR = tempfile.gettempdir()
LEADS_FILE = os.path.join(TEMP_DIR, "orquesta_leads.json")
CONVERSATIONS_FILE = os.path.join(TEMP_DIR, "orquesta_conversations.json")

app = Flask(__name__)

def log_msg(msg):
    ts = datetime.now().isoformat()
    print(f"[{ts}] {msg}")

def load_conversations():
    try:
        if os.path.exists(CONVERSATIONS_FILE):
            with open(CONVERSATIONS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        log_msg(f"Error loading conversations: {e}")
    return {}

def save_conversations(data):
    try:
        with open(CONVERSATIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_msg(f"Error saving conversations: {e}")

def load_leads():
    try:
        if os.path.exists(LEADS_FILE):
            with open(LEADS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        log_msg(f"Error loading leads: {e}")
    return []

def save_leads(leads):
    try:
        with open(LEADS_FILE, 'w') as f:
            json.dump(leads, f, indent=2)
    except Exception as e:
        log_msg(f"Error saving leads: {e}")

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Webhook de Twilio"""
    
    log_msg("📨 Webhook called")
    resp = MessagingResponse()
    
    try:
        incoming_msg = request.values.get('Body', '').strip()
        sender = request.values.get('From', '').replace('whatsapp:', '')
        
        log_msg(f"👤 From: {sender}")
        log_msg(f"💬 Message: {incoming_msg[:100]}")
        
        if not incoming_msg:
            resp.message("Hola 👋")
            return str(resp)
        
        conversations = load_conversations()
        
        # New conversation
        if sender not in conversations:
            log_msg(f"🆕 New conversation from {sender}")
            conversations[sender] = {
                'step': 0,
                'data': {},
                'started_at': datetime.now().isoformat()
            }
            
            msg = "🎵 ¡Hola! Bienvenido a Orquesta.\n\nVamos a conocer tu negocio en 3 preguntas rápidas.\n\n¿Cuál es el nombre de tu empresa?"
            resp.message(msg)
            save_conversations(conversations)
            log_msg(f"✅ Welcome sent")
            return str(resp)
        
        conv = conversations[sender]
        step = conv['step']
        
        # Step 1: Company
        if step == 0:
            conv['data']['empresa'] = incoming_msg
            conv['step'] = 1
            msg = "¡Perfecto! 📧\n\n¿Qué servicio de Orquesta te interesa?\n\n1️⃣ WhatsApp & CRM\n2️⃣ E-commerce Analytics\n3️⃣ Market Research"
            resp.message(msg)
            save_conversations(conversations)
            log_msg(f"✅ Step 1: {incoming_msg}")
            return str(resp)
        
        # Step 2: Service
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
            log_msg(f"✅ Step 2: {conv['data']['servicio']}")
            return str(resp)
        
        # Step 3: Save lead
        elif step == 2:
            conv['data']['empleados'] = incoming_msg
            conv['step'] = 3
            
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
            
            log_msg(f"💾 Lead saved: {new_lead['nombre']}")
            
            final_msg = f"✅ ¡Listo!\n\n📱 {conv['data']['empresa']}\n🎯 {conv['data']['servicio']}\n👥 {conv['data']['empleados']} empleados\n\nNuestro equipo te contactará en 24h.\n\n¿Preguntas? Escribe 💬"
            resp.message(final_msg)
            save_conversations(conversations)
            
            return str(resp)
        
        return str(resp)
        
    except Exception as e:
        log_msg(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        resp = MessagingResponse()
        resp.message("Error. Intenta de nuevo.")
        return str(resp)

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok', 'leads_file': LEADS_FILE}, 200

if __name__ == '__main__':
    log_msg("🚀 Bot started")
    log_msg(f"📁 Temp dir: {TEMP_DIR}")
    log_msg(f"📝 Leads: {LEADS_FILE}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
