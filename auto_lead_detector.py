#!/usr/bin/env python3
"""
Auto Lead Detector
Monitorea mensajes del bot y automáticamente guarda leads cuando detecta que fueron calificados
"""

import json
import os
import re
from datetime import datetime
from save_lead import save_lead

def detect_lead_completion(message_history):
    """
    Detecta si un lead fue completado basándose en los mensajes
    Busca patrones como:
    - Bot hizo 3 preguntas
    - Usuario respondió las 3 preguntas
    - Bot ofreció agendar
    """
    
    if len(message_history) < 8:  # Mínimo: 3 preguntas + 3 respuestas + 2 respuestas del bot
        return None
    
    # Buscar respuestas de usuario
    empresa = None
    servicio = None
    empleados = None
    
    messages = "\n".join([msg.get("text", "").lower() for msg in message_history])
    
    # Patrones para detectar respuestas
    patrones = {
        "empresa": [
            r"(?:se dedica|negocio|empresa|rubro).*?([a-záéíóú\s]+)",
            r"(oftalmología|ecommerce|consultora|agencia|tecnología|servicios)"
        ],
        "servicio": [
            r"(?:automatizar|mejorar).*?(whatsapp|crm|ecommerce|mercado)",
            r"(automatización|consultoría|análisis)"
        ],
        "empleados": r"(\d+)\s*(?:empleados|personas|gente)"
    }
    
    # Buscar empresa
    for patron in patrones["empresa"]:
        match = re.search(patron, messages)
        if match:
            empresa = match.group(1).strip()
            break
    
    # Buscar servicio
    for patron in patrones["servicio"]:
        match = re.search(patron, messages)
        if match:
            servicio = match.group(1).strip()
            break
    
    # Buscar empleados
    match = re.search(patrones["empleados"], messages)
    if match:
        empleados = match.group(1)
    
    # Si encontramos los 3 datos, es un lead completado
    if empresa and servicio:
        return {
            "empresa": empresa,
            "servicio": servicio,
            "empleados": empleados or "No especificado"
        }
    
    return None

def monitor_telegram_leads(session_history):
    """
    Monitorea un historial de sesión y detecta leads completados
    """
    
    completed_leads = []
    processed_ids = set()
    
    # Cargar leads ya procesados
    leads_file = os.path.expanduser("~/.openclaw/workspace/leads.json")
    try:
        with open(leads_file, "r") as f:
            existing_leads = json.load(f)
            # Marcar como procesados
            for lead in existing_leads:
                processed_ids.add(f"{lead.get('nombre')}{lead.get('apellido')}")
    except:
        existing_leads = []
    
    # Buscar patrones de leads completados
    # Este es un ejemplo básico - necesitaría integración con OpenClaw
    
    return completed_leads

def auto_capture_from_logs():
    """
    Automáticamente captura leads de los logs de conversación
    Uso: python auto_lead_detector.py
    """
    
    print("🔍 Monitoreando conversaciones para detectar leads...")
    print("⚠️  Nota: Esta función requiere integración con OpenClaw API")
    print("Por ahora usa: guardar_lead.sh <nombre> <apellido> <empresa> <servicio>")

if __name__ == "__main__":
    auto_capture_from_logs()
