#!/usr/bin/env python3
"""
Telegram Bot Inteligente
- Personalización por rubro
- Calendly automático
- Conversación continuada post-booking
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

# Definir preguntas personalizadas por rubro
RUBRO_CONFIG = {
    "oftalmología": {
        "pregunta_2": "¿Qué aspecto de tu consultoría oftalmológica querés mejorar?\n\n(Ej: gestión de citas, historiales de pacientes, seguimiento post-consulta)",
        "keywords": ["oftalmología", "oftalmologico", "oftalmologica", "oftalmólogo", "oftalmologo", "ojo", "ojos", "vista"]
    },
    "ecommerce": {
        "pregunta_2": "¿Qué parte de tu ecommerce querés automatizar?\n\n(Ej: pedidos, seguimiento de envíos, gestión de inventario, carrito abandonado)",
        "keywords": ["ecommerce", "tienda", "tienda online", "shop", "amazon", "mercado libre"]
    },
    "consultora": {
        "pregunta_2": "¿Qué procesos internos querés optimizar?\n\n(Ej: asignación de proyectos, reportes de horas, comunicación con clientes)",
        "keywords": ["consultora", "consultoría", "consulting", "agencia"]
    },
    "veterinaria": {
        "pregunta_2": "¿Qué procesos veterinarios querés mejorar?\n\n(Ej: citas de mascotas, historiales médicos, recordatorios de vacunas)",
        "keywords": ["veterinaria", "veterinario", "mascotas", "perros", "gatos", "animales"]
    },
    "farmacia": {
        "pregunta_2": "¿Qué procesos farmacéuticos querés automatizar?\n\n(Ej: gestión de recetas, stock de medicamentos, entregas a domicilio)",
        "keywords": ["farmacia", "farmacéutico", "medicinas", "medicamentos"]
    },
    "educación": {
        "pregunta_2": "¿Qué procesos educativos querés optimizar?\n\n(Ej: inscripciones, seguimiento de estudiantes, tareas, comunicación con padres)",
        "keywords": ["educación", "escuela", "colegio", "universidad", "profesor", "estudiante"]
    }
}

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
        print(f"❌ Error: {e}")
        return {"result": []}

def detectar_rubro(text):
    """Detecta el rubro según la respuesta del usuario"""
    
    text_lower = text.lower()
    
    for rubro, config in RUBRO_CONFIG.items():
        for keyword in config["keywords"]:
            if keyword in text_lower:
                return rubro
    
    return None

def obtener_pregunta_personalizada(rubro, numero):
    """Obtiene la pregunta personalizada según el rubro"""
    
    if numero == 2 and rubro in RUBRO_CONFIG:
        return RUBRO_CONFIG[rubro]["pregunta_2"]
    
    # Preguntas genéricas
    if numero == 1:
        return "<b>1️⃣ ¿A qué se dedica tu empresa?</b>"
    elif numero == 2:
        return "<b>2️⃣ ¿Qué proceso te gustaría automatizar?</b>\n\n(Por ejemplo: pedidos, consultas, facturación, etc)"
    elif numero == 3:
        return "<b>3️⃣ ¿Cuántos empleados tiene tu empresa?</b>"

def process_message(chat_id, user_name, text):
    """Procesa un mensaje y gestiona la conversación"""
    
    # Ignorar comandos
    if text.startswith('/'):
        return
    
    # Inicializar conversación si no existe
    if chat_id not in conversations:
        conversations[chat_id] = {
            "nombre": user_name,
            "empresa": None,
            "rubro": None,
            "servicio": None,
            "empleados": None,
            "created_at": datetime.now().isoformat(),
            "guardado": False,
            "stage": 0,  # 0: inicio, 1: empresa, 2: servicio, 3: empleados, 4: completado
            "post_booking": False  # True después de que agenda en Calendly
        }
        
        # Iniciar conversación
        send_message(
            chat_id,
            f"¡Hola {user_name}! 👋\n\nBienvenido a <b>Orquesta AI</b> 🤖\n\nSomos una plataforma de automatización inteligente para tu negocio.\n\nTe haré 3 preguntas rápidas y luego te ofreceremos una demo personalizada.\n\n" +
            obtener_pregunta_personalizada(None, 1)
        )
        return
    
    conv = conversations[chat_id]
    
    # Si ya completó las 3 preguntas, es conversación libre (post-booking)
    if conv['stage'] >= 4:
        handle_post_booking_message(chat_id, user_name, text)
        return
    
    # PREGUNTA 1: EMPRESA
    if conv['empresa'] is None:
        conv['empresa'] = text.strip().title()
        conv['rubro'] = detectar_rubro(text)
        conv['stage'] = 1
        
        print(f"   ✓ Empresa: {conv['empresa']}")
        if conv['rubro']:
            print(f"   ✓ Rubro detectado: {conv['rubro']}")
        
        send_message(
            chat_id,
            f"¡Perfecto! 📋 <b>{conv['empresa']}</b>\n\n" +
            obtener_pregunta_personalizada(conv['rubro'], 2)
        )
        return
    
    # PREGUNTA 2: SERVICIO
    if conv['servicio'] is None:
        conv['servicio'] = text.strip().title()
        conv['stage'] = 2
        
        print(f"   ✓ Servicio: {conv['servicio']}")
        
        send_message(
            chat_id,
            f"Excelente 🎯 Automatizar <b>{conv['servicio']}</b> va a mejorar mucho tu eficiencia.\n\n" +
            obtener_pregunta_personalizada(conv['rubro'], 3)
        )
        return
    
    # PREGUNTA 3: EMPLEADOS
    if conv['empleados'] is None:
        numeros = re.findall(r'\d+', text)
        if numeros:
            conv['empleados'] = int(numeros[0])
            conv['stage'] = 3
            
            print(f"   ✓ Empleados: {conv['empleados']}")
            
            # GUARDAR AUTOMÁTICAMENTE
            save_lead_auto(chat_id, conv, user_name)
        else:
            send_message(chat_id, "Por favor, responde con un número (ej: 5, 10, 25)")
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
        conv['stage'] = 4
        conv['post_booking'] = False
        
        print(f"   ✅ LEAD GUARDADO - HubSpot sincronizará en <1 minuto")
        
        # Responder al usuario con Calendly
        rubro_text = f" de {conv['rubro'].title()}" if conv['rubro'] else ""
        
        send_message(
            chat_id,
            f"🎉 ¡Perfecto {user_name}!\n\n"
            f"<b>Resumen de tu consulta:</b>\n"
            f"• <b>Empresa:</b> {empresa}\n"
            f"• <b>Automatizar:</b> {servicio}\n"
            f"• <b>Empleados:</b> {conv['empleados']}\n\n"
            f"Nuestro equipo de especialistas{rubro_text} preparará una propuesta personalizada para ti.\n\n"
            f"<b>📅 ¿Querés agendar una demo?</b>\n"
            f"<a href='{CALENDLY_LINK}'>Reservá tu slot aquí</a>\n\n"
            f"Mientras tanto, ¿tenés alguna pregunta sobre la automatización? Estoy aquí para ayudarte 👋"
        )
        
    except Exception as e:
        print(f"   ❌ Error al guardar: {e}")
        send_message(chat_id, "Hubo un error al procesar tu información. Por favor intenta más tarde.")

def handle_post_booking_message(chat_id, user_name, text):
    """Maneja mensajes después de que el usuario completa las 3 preguntas"""
    
    # Responder de forma inteligente y amable
    text_lower = text.lower()
    
    # Detectar preguntas comunes
    if any(word in text_lower for word in ["precio", "costo", "valor", "cuesta", "cuanto"]):
        send_message(
            chat_id,
            "💰 <b>Sobre los precios:</b>\n\n"
            "Ofrecemos planes personalizados según el tamaño y complejidad de tu empresa.\n\n"
            "Lo mejor es que lo discutas directamente en la demo, donde ajustamos la propuesta a tu presupuesto.\n\n"
            "¿Hay algo más en lo que pueda ayudarte? 😊"
        )
    
    elif any(word in text_lower for word in ["tiempo", "cuanto tarda", "implementación", "cuanto demora"]):
        send_message(
            chat_id,
            "⏱️ <b>Sobre la implementación:</b>\n\n"
            "Generalmente entre 2-4 semanas dependiendo de la complejidad.\n\n"
            "En la demo veremos tu caso específico y te daremos un timeline exacto.\n\n"
            "¿Otra pregunta? Estoy atento 👂"
        )
    
    elif any(word in text_lower for word in ["integracion", "integración", "conectar", "sincronizar"]):
        send_message(
            chat_id,
            "🔗 <b>Sobre integraciones:</b>\n\n"
            "Orquesta se integra con: WhatsApp, Telegram, CRM, ERP, bases de datos y más.\n\n"
            "Veremos en la demo qué herramientas ya usas y cómo las conectamos.\n\n"
            "¿Necesitas conectar algo específico? 🤔"
        )
    
    elif any(word in text_lower for word in ["gracias", "ok", "dale", "perfecto", "listo"]):
        send_message(
            chat_id,
            f"¡Gracias {user_name}! 🙌\n\n"
            f"Nos vemos pronto en la demo. Cualquier duda, escribime aquí.\n\n"
            f"Mientras tanto, podés revisar más info en <b>orquestaai.com</b> 🚀"
        )
    
    else:
        # Respuesta genérica pero amable
        send_message(
            chat_id,
            f"Buena pregunta {user_name}! 🤔\n\n"
            f"Esa es una excelente pregunta para la demo. Nuestro equipo de especialistas podrá darte detalles.\n\n"
            f"Mientras tanto, si tenés otras dudas, ¡adelante! Estoy aquí para ayudarte. 😊"
        )

def main():
    """Loop principal"""
    
    offset = None
    
    print("=" * 60)
    print("🤖 TELEGRAM BOT INTELIGENTE ACTIVO")
    print("=" * 60)
    print(f"   Bot: @orquestai_bot")
    print(f"   Modo: Personalizado + Atento")
    print(f"   Calendly: {CALENDLY_LINK}")
    print("=" * 60)
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update['update_id'] + 1
                    
                    if 'message' not in update:
                        continue
                    
                    msg = update['message']
                    
                    if 'text' not in msg:
                        continue
                    
                    chat_id = msg['chat']['id']
                    user_name = msg['from'].get('first_name', 'Usuario')
                    text = msg['text'].strip()
                    
                    print(f"\n📱 {user_name} → {text}")
                    
                    process_message(chat_id, user_name, text)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n✅ Bot detenido")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
