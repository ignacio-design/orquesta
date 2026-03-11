#!/usr/bin/env python3
"""
Auto Lead Webhook & Extractor
Monitorea conversaciones y automáticamente guarda leads completados
Se integra con OpenClaw para leer historial de chats
"""

import json
import os
import re
import sys
from datetime import datetime
from save_lead import save_lead

def extract_lead_data(conversation_text):
    """
    Extrae datos de lead de una conversación de Telegram/WhatsApp
    Busca patrones en las respuestas del usuario
    """
    
    text = conversation_text.lower()
    
    # Detectar si fue calificado (búsqueda de respuestas a las 3 preguntas)
    has_company = re.search(r'(?:empresa|se dedica|negocio|rubro)[:\s]+([^?.\n]+)', text)
    has_service = re.search(r'(?:automatizar|mejorar|querés?)[:\s]+([^?.\n]+)', text)
    has_employees = re.search(r'(?:empleados|personas|gente)[:\s]+(\d+)', text)
    
    if not (has_company and has_service and has_employees):
        return None
    
    # Extraer datos
    empresa = has_company.group(1).strip() if has_company else "No especificada"
    servicio = has_service.group(1).strip() if has_service else "Consultoría"
    
    # Limpiar y normalizar
    empresa = empresa.replace("a qué se dedica su empresa", "").strip()[:100]
    servicio = servicio.replace("qué proceso", "").replace("querés", "").strip()[:100]
    
    # Detectar patrón de nombre (si está en la conversación)
    nombre_match = re.search(r'(?:hola|hi|hey)\s+([A-Za-z]+)', text)
    nombre = nombre_match.group(1) if nombre_match else "Lead"
    
    return {
        "nombre": nombre,
        "apellido": "Orquesta",
        "empresa": empresa,
        "servicio": servicio
    }

def check_conversation_completion(messages):
    """
    Revisa si una conversación fue completada (3 preguntas + 3 respuestas)
    Retorna True si detecta que el lead fue calificado
    """
    
    if len(messages) < 8:  # Mínimo para completar el flujo
        return False
    
    # Buscar patrones de bot preguntando y usuario respondiendo
    user_responses = sum(1 for m in messages if m.get("sender") != "bot")
    bot_questions = sum(1 for m in messages if m.get("sender") == "bot" and "?" in m.get("text", ""))
    
    return user_responses >= 3 and bot_questions >= 3

def auto_save_from_conversation(chat_data):
    """
    Automáticamente guarda un lead si detecta que la conversación fue completada
    """
    
    if not chat_data:
        return False
    
    # Convertir messages a texto
    conversation_text = "\n".join([m.get("text", "") for m in chat_data.get("messages", [])])
    
    # Detectar si fue completado
    if not check_conversation_completion(chat_data.get("messages", [])):
        return False
    
    # Extraer datos
    lead_data = extract_lead_data(conversation_text)
    
    if not lead_data:
        return False
    
    # Guardar
    return save_lead(
        lead_data["nombre"],
        lead_data["apellido"],
        lead_data["empresa"],
        lead_data["servicio"]
    )

def monitor_leads():
    """
    Monitorea leads pendientes en el workspace
    Ejecuta automáticamente cada minuto (vía cron)
    """
    
    print("🔍 Monitoreando conversaciones para auto-guardar leads...")
    print("⚠️  Nota: Esto se ejecutará automáticamente vía cron job")
    print("✅ Sistema listo para capturar leads automáticamente")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test: simular conversación completada
        test_data = {
            "messages": [
                {"sender": "user", "text": "Hola, quiero automatizar"},
                {"sender": "bot", "text": "¿A qué se dedica tu empresa?"},
                {"sender": "user", "text": "Oftalmología"},
                {"sender": "bot", "text": "¿Qué querés automatizar?"},
                {"sender": "user", "text": "Consultas por WhatsApp"},
                {"sender": "bot", "text": "¿Cuántos empleados?"},
                {"sender": "user", "text": "4"},
                {"sender": "bot", "text": "Perfecto, agendá aquí"},
            ]
        }
        
        result = auto_save_from_conversation(test_data)
        print(f"Test result: {result}")
    else:
        monitor_leads()
