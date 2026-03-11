#!/usr/bin/env python3
"""Telegram Bot - Versión final limpia y funcional"""

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
    """Envía mensaje limpio"""
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=5)
    except:
        pass

def get_updates(offset=None):
    """Obtiene mensajes"""
    params = {"offset": offset, "timeout": 30} if offset else {"timeout": 30}
    try:
        return requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35).json()
    except:
        return {"result": []}

def limpiar_texto(text):
    """Limpia texto - solo primeras 50 caracteres, sin saltos"""
    return text.strip()[:50].replace('\n', ' ')

def extraer_numero(text):
    """Extrae el PRIMER número de un texto"""
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None

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
            "completado": False,
            "stage": 0
        }
        
        send_message(chat_id, f"Hola {user_name}\n\n¿A qué se dedica tu empresa?")
        return
    
    conv = conversations[chat_id]
    
    # Si ya completó: responder preguntas
    if conv['completado']:
        text_lower = text.lower()
        if any(w in text_lower for w in ["precio", "costo", "valor", "cuanto"]):
            send_message(chat_id, "Los precios se ajustan según tu proyecto. Lo vemos en la llamada.")
        elif any(w in text_lower for w in ["tiempo", "cuanto tarda", "implementar", "demora"]):
            send_message(chat_id, "Entre 2-4 semanas. Te daremos un timeline exacto en la demo.")
        elif any(w in text_lower for w in ["integracion", "conectar", "sincronizar"]):
            send_message(chat_id, "Nos integramos con WhatsApp, CRM, bases de datos y más.")
        else:
            send_message(chat_id, "Excelente pregunta. Lo vemos en la demo.")
        return
    
    # PREGUNTA 1: EMPRESA
    if conv['empresa'] is None:
        conv['empresa'] = limpiar_texto(text)
        send_message(chat_id, "¿Qué proceso te gustaría automatizar?")
        return
    
    # PREGUNTA 2: SERVICIO
    if conv['servicio'] is None:
        conv['servicio'] = limpiar_texto(text)
        send_message(chat_id, "¿Cuántos empleados tiene tu empresa? (número)")
        return
    
    # PREGUNTA 3: EMPLEADOS
    if conv['empleados'] is None:
        num = extraer_numero(text)
        if num and num > 0:
            conv['empleados'] = num
            conv['completado'] = True
            
            # Guardar en leads.json
            try:
                save_lead(user_name, "Telegram", conv['empresa'], conv['servicio'])
                print(f"✅ Lead guardado: {user_name} - {conv['empresa']}")
            except Exception as e:
                print(f"❌ Error guardando: {e}")
            
            send_message(
                chat_id,
                f"Perfecto. Agendar llamada:\n\n{CALENDLY_LINK}\n\n¿Alguna pregunta?"
            )
        else:
            send_message(chat_id, "Por favor, responde con un número (ej: 5, 10, 25)")

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
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
