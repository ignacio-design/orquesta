#!/usr/bin/env python3
"""
Wati WhatsApp Bot - Orquesta
"""

from flask import Flask, request, jsonify
import json
import os
import requests
from datetime import datetime
import tempfile

# Wati Config
WATI_API_ENDPOINT = "https://live-mt-server.wati.io/10111126"
WATI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6ImlnbmFjaW9Ab3JxdWVzdGEtYWkuY29tIiwibmFtZWlkIjoiaWduYWNpb0BvcnF1ZXN0YS1haS5jb20iLCJlbWFpbCI6ImlnbmFjaW9Ab3JxdWVzdGEtYWkuY29tIiwiYXV0aF90aW1lIjoiMDMvMTEvMjAyNiAyMjowNDo0MyIsInRlbmFudF9pZCI6IjEwMTExMTI2IiwiZGJfbmFtZSI6Im10LXByb2QtVGVuYW50cyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFETUlOSVNUUkFUT1IiLCJleHAiOjI1MzQwMjMwMDgwMCwiaXNzIjoiQ2xhcmVfQUkiLCJhdWQiOiJDbGFyZV9BSSJ9.PUN1SzoaSPnuixYw9qD2I4zQoDB7LPUJuE0Dy6c6Xwo"

# Files in /tmp for Render compatibility
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

def send_wati_message(phone, message):
    """Envía mensaje por Wati"""
    try:
        headers = {
            "Authorization": WATI_TOKEN,
            "Content-Type": "application/json"
        }
        data = {
            "phoneNumber": phone,
            "messageText": message
        }
        response = requests.post(
            f"{WATI_API_ENDPOINT}/api/send/message",
            json=data,
            headers=headers,
            timeout=10
        )
        log_msg(f"Wati response: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        log_msg(f"Error sending Wati message: {e}")
        return False

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Webhook de Wati"""
    
    log_msg("📨 Wati webhook received")
    
    try:
        data = request.json
        
        # Parsear mensaje de Wati
        incoming_msg = data.get('messageBody', '').strip()
        sender = data.get('waNumber', '')
        
        log_msg(f"👤 From: {sender}")
        log_msg(f"💬 Message: {incoming_msg[:100]}")
        
        if not sender or not incoming_msg:
            return jsonify({"status": "ok"}), 200
        
        # Cargar conversaciones
        conversations = load_conversations()
        
        # Nueva conversación
        if sender not in conversations:
            log_msg(f"🆕 New conversation from {sender}")
            conversations[sender] = {
                'step': 0,
                'data': {},
                'started_at': datetime.now().isoformat()
            }
            
            msg = "🎵 ¡Hola! Bienvenido a Orquesta.\n\nVamos a conocer tu negocio en 3 preguntas rápidas.\n\n¿Cuál es el nombre de tu empresa?"
            send_wati_message(sender, msg)
            save_conversations(conversations)
            log_msg(f"✅ Welcome sent")
            return jsonify({"status": "ok"}), 200
        
        conv = conversations[sender]
        step = conv['step']
        
        # Step 1: Company
        if step == 0:
            conv['data']['empresa'] = incoming_msg
            conv['step'] = 1
            msg = "¡Perfecto! 📧\n\n¿Qué servicio de Orquesta te interesa?\n\n1️⃣ WhatsApp & CRM\n2️⃣ E-commerce Analytics\n3️⃣ Market Research"
            send_wati_message(sender, msg)
            save_conversations(conversations)
            log_msg(f"✅ Step 1: {incoming_msg}")
            return jsonify({"status": "ok"}), 200
        
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
            send_wati_message(sender, msg)
            save_conversations(conversations)
            log_msg(f"✅ Step 2: {conv['data']['servicio']}")
            return jsonify({"status": "ok"}), 200
        
        # Step 3: Save lead
        elif step == 2:
            conv['data']['empleados'] = incoming_msg
            conv['step'] = 3
            
            # Save lead
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
            send_wati_message(sender, final_msg)
            save_conversations(conversations)
            
            return jsonify({"status": "ok"}), 200
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        log_msg(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    log_msg("🚀 Wati WhatsApp Bot started")
    log_msg(f"📊 Endpoint: {WATI_API_ENDPOINT}")
    log_msg(f"📝 Leads: {LEADS_FILE}")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
