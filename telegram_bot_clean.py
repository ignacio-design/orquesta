#!/usr/bin/env python3
"""
Telegram Bot Limpio - Solo lo necesario, profesional
"""

import requests
import json
import re
import time
from datetime import datetime
from save_lead import save_lead

BOT_TOKEN = "8689609607:AAEvfHhG6j83OwZM2F2EUOYTQK9QJygFsXE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
CALENDLY_LINK = "https://calendly.com/ignacio-orquesta-ai/30min"

conversations = {}

def send_message(chat_id, text):
    """Envía un mensaje"""
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=payload)
    except:
        pass

def get_updates(offset=None):
    """Obtiene mensajes"""
    params = {"offset": offset} if offset else {}
    try:
        return requests.get(f"{BASE_URL}/getUpdates", params=params).json()
    except:
        return {"result": []}

def process_message(chat_id, user_name, text):
    """Procesa mensaje"""
    
    if text.startswith('/'):
        return
    
    if chat_id not in conversations:
        conversations[chat_id] = {
            "nombre": user_name,
            "empresa": None,
            "servicio": None,
            "empleados": None,
            "guardado": False,
            "stage": 0
        }
        
        send_message(chat_id, "Hola " + user_name + "\n\n¿A qué se dedica tu empresa?")
        return
    
    conv = conversations[chat_id]
    
    # Si está completo, responder preguntas
    if conv['stage'] >= 3:
        text_lower = text.lower()
        if any(w in text_lower for w in ["precio", "costo", "valor"]):
            send_message(chat_id, "Los precios se ajustan según tu proyecto. Lo vemos en detalle en la llamada.")
        elif any(w in text_lower for w in ["tiempo", "cuanto", "implementar"]):
            send_message(chat_id, "Generalmente entre 2-4 semanas. Te daremos un timeline exacto en la demo.")
        elif any(w in text_lower for w in ["integracion", "conectar"]):
            send_message(chat_id, "Nos integramos con WhatsApp, CRM, bases de datos y más. Vemos lo que necesitas en la demo.")
        else:
            send_message(chat_id, "Excelente pregunta. Lo vemos en detalle en la demo.")
        return
    
    # PREGUNTA 1
    if conv['empresa'] is None:
        conv['empresa'] = text.strip()
        conv['stage'] = 1
        send_message(chat_id, "¿Qué proceso específico te gustaría automatizar?")
        return
    
    # PREGUNTA 2
    if conv['servicio'] is None:
        conv['servicio'] = text.strip()
        conv['stage'] = 2
        send_message(chat_id, "¿Cuántos empleados tiene tu empresa?")
        return
    
    # PREGUNTA 3
    if conv['empleados'] is None:
        numeros = re.findall(r'\d+', text)
        if numeros:
            conv['empleados'] = int(numeros[0])
            conv['stage'] = 3
            
            try:
                save_lead(user_name, f"Telegram_{chat_id}", conv['empresa'], conv['servicio'])
                conv['guardado'] = True
            except:
                pass
            
            send_message(
                chat_id,
                f"Perfecto. Te ofrecemos una llamada para personalizar la propuesta.\n\n{CALENDLY_LINK}\n\n¿Alguna pregunta mientras tanto?"
            )
        else:
            send_message(chat_id, "Responde con un número, por favor (ej: 5, 10, 25)")

def main():
    offset = None
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update['update_id'] + 1
                    
                    if 'message' not in update or 'text' not in update['message']:
                        continue
                    
                    msg = update['message']
                    chat_id = msg['chat']['id']
                    user_name = msg['from'].get('first_name', 'Usuario')
                    text = msg['text'].strip()
                    
                    process_message(chat_id, user_name, text)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            break
        except:
            time.sleep(5)

if __name__ == "__main__":
    main()
