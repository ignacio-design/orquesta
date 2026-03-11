#!/usr/bin/env python3
"""
Telegram Bot - Auto-respuesta y guardado automático
Usa polling (sin webhooks)
"""

import requests
import json
import re
import time
from datetime import datetime
from save_lead import save_lead

# Token del bot
BOT_TOKEN = "8689609607:AAEvfHhG6j83OwZM2F2EUOYTQK9QJygFsXE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Estado de conversaciones
conversations = {}

def send_message(chat_id, text, reply_markup=None):
    """Envía un mensaje a Telegram"""
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(f"{BASE_URL}/sendMessage", json=payload)
        return response.json()
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return None

def get_updates(offset=None):
    """Obtiene los últimos mensajes de Telegram"""
    
    params = {}
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(f"{BASE_URL}/getUpdates", params=params)
        return response.json()
    except Exception as e:
        print(f"❌ Error obteniendo updates: {e}")
        return {"result": []}

def process_message(chat_id, user_name, text):
    """Procesa un mensaje y detecta cuando está completo"""
    
    # Inicializar conversación si no existe
    if chat_id not in conversations:
        conversations[chat_id] = {
            "nombre": user_name,
            "empresa": None,
            "servicio": None,
            "empleados": None,
            "created_at": datetime.now().isoformat(),
            "guardado": False,
            "stage": 0  # Etapa de la conversación
        }
        
        # Iniciar conversación
        send_message(
            chat_id,
            f"¡Hola {user_name}! 👋\n\nBienvenido a <b>Orquesta AI</b>.\n\nSomos una plataforma de automatización inteligente para tu negocio.\n\nTe haré 3 preguntas rápidas:\n\n<b>1️⃣ ¿A qué se dedica tu empresa?</b>"
        )
        return
    
    conv = conversations[chat_id]
    
    # PREGUNTA 1: EMPRESA
    if conv['empresa'] is None:
        conv['empresa'] = text.strip().title()
        print(f"   ✓ Empresa: {conv['empresa']}")
        
        send_message(
            chat_id,
            f"¡Perfecto! 📋\n\n<b>{conv['empresa']}</b>\n\nAhora la siguiente pregunta:\n\n<b>2️⃣ ¿Qué proceso te gustaría automatizar?</b>\n\n(Por ejemplo: pedidos, consultas, facturación, etc)"
        )
        return
    
    # PREGUNTA 2: SERVICIO
    if conv['servicio'] is None:
        conv['servicio'] = text.strip().title()
        print(f"   ✓ Servicio: {conv['servicio']}")
        
        send_message(
            chat_id,
            f"Excelente 🎯\n\nAutomatizar <b>{conv['servicio']}</b> va a mejorar mucho tu eficiencia.\n\nÚltima pregunta:\n\n<b>3️⃣ ¿Cuántos empleados tiene tu empresa?</b>"
        )
        return
    
    # PREGUNTA 3: EMPLEADOS
    if conv['empleados'] is None:
        numeros = re.findall(r'\d+', text)
        if numeros:
            conv['empleados'] = int(numeros[0])
            print(f"   ✓ Empleados: {conv['empleados']}")
            
            # GUARDAR AUTOMÁTICAMENTE
            save_lead_auto(chat_id, conv, user_name)
        else:
            send_message(chat_id, "Por favor, responde con un número (ej: 5, 10, 25)")
            return
        
        return

def save_lead_auto(chat_id, conv, user_name):
    """Guarda el lead automáticamente"""
    
    try:
        nombre = user_name
        apellido = f"Telegram_{chat_id}"
        empresa = conv['empresa']
        servicio = conv['servicio']
        
        print(f"   💾 GUARDANDO: {nombre} de {empresa}")
        
        # Guardar en leads.json
        save_lead(nombre, apellido, empresa, servicio)
        
        # Marcar como guardado
        conv['guardado'] = True
        
        print(f"   ✅ LEAD GUARDADO - HubSpot sincronizará en <1 minuto")
        
        # Responder al usuario
        send_message(
            chat_id,
            f"🎉 ¡Perfecto {nombre}!\n\n<b>Resumen de tu consulta:</b>\n"
            f"• Empresa: {empresa}\n"
            f"• Automatizar: {servicio}\n"
            f"• Empleados: {conv['empleados']}\n\n"
            f"Nos pondremos en contacto en breve con una propuesta personalizada.\n\n"
            f"¿Querés agendar una demo? Usa este link:\n"
            f"<a href='https://calendly.com/ignacio-orquesta-ai/30min'>📅 Agendar Demo</a>"
        )
        
    except Exception as e:
        print(f"   ❌ Error al guardar: {e}")
        send_message(chat_id, "Hubo un error al procesar tu información. Por favor intenta más tarde.")

def main():
    """Loop principal"""
    
    offset = None
    
    print("=" * 60)
    print("🤖 TELEGRAM BOT AUTOMÁTICO ACTIVO")
    print("=" * 60)
    print(f"   Bot: @orquestai_bot")
    print(f"   Estado: Escuchando mensajes...")
    print("=" * 60)
    
    while True:
        try:
            # Obtener nuevos mensajes
            updates = get_updates(offset)
            
            if updates.get("ok"):
                for update in updates.get("result", []):
                    
                    # Actualizar offset
                    offset = update['update_id'] + 1
                    
                    # Procesar solo mensajes de texto
                    if 'message' not in update:
                        continue
                    
                    msg = update['message']
                    
                    # Ignorar comandos
                    if 'text' not in msg or msg['text'].startswith('/'):
                        continue
                    
                    chat_id = msg['chat']['id']
                    user_name = msg['from'].get('first_name', 'Usuario')
                    text = msg['text'].strip()
                    
                    print(f"\n📱 MENSAJE: {user_name} → {text}")
                    
                    # Procesar
                    process_message(chat_id, user_name, text)
            
            # Esperar un poco antes de siguiente request
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n✅ Bot detenido")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
