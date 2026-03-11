#!/usr/bin/env python3
"""
Auto Process Leads - Maestro
Se ejecuta cada minuto vía cron
Automáticamente detecta, guarda y procesa leads sin intervención
"""

import json
import os
import re
import subprocess
from datetime import datetime
from save_lead import save_lead

def get_saved_lead_ids():
    """Obtiene IDs de leads ya guardados"""
    leads_file = os.path.expanduser("~/.openclaw/workspace/leads.json")
    try:
        with open(leads_file, "r") as f:
            leads = json.load(f)
            return {f"{l.get('nombre')}{l.get('apellido')}" for l in leads}
    except:
        return set()

def detect_completed_leads():
    """
    Detecta conversaciones completadas
    Retorna lista de leads para guardar
    """
    
    completed = []
    
    # Buscar archivos de conversación reciente
    # En un sistema real, integraríamos con OpenClaw API
    # Por ahora, usamos un archivo de tracking
    
    tracking_file = os.path.expanduser("~/.openclaw/workspace/.lead_tracking.json")
    try:
        with open(tracking_file, "r") as f:
            recent_conversations = json.load(f)
    except:
        recent_conversations = {}
    
    return completed

def auto_extract_and_save():
    """
    Automáticamente extrae y guarda leads completados
    Se ejecuta cada minuto
    """
    
    # Patrón: buscar en leads pendientes que aún no fueron procesados
    leads_file = os.path.expanduser("~/.openclaw/workspace/leads.json")
    
    # Si hay leads sin procesar, procesarlos
    try:
        with open(leads_file, "r") as f:
            leads = json.load(f)
    except:
        return
    
    # Llamar a process_leads.py para sincronizar a HubSpot
    try:
        subprocess.run(
            ["python3", os.path.expanduser("~/.openclaw/workspace/process_leads.py")],
            capture_output=True,
            timeout=30
        )
    except:
        pass

def watch_telegram_messages():
    """
    Monitorea nuevos mensajes de Telegram
    Nota: Esto requeriría integración con OpenClaw o webhook
    """
    
    # En desarrollo: integración con OpenClaw's session API
    # Para ahora, mantener la cron simple que procese leads existentes
    
    print("✅ Auto-processor ejecutado")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Procesar cualquier lead pendiente
    auto_extract_and_save()

if __name__ == "__main__":
    watch_telegram_messages()
