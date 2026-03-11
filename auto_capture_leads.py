#!/usr/bin/env python3
"""
Auto Capture Leads from Telegram/WhatsApp
Monitorea conversaciones y automáticamente guarda leads calificados
"""

import json
import os
import sys
from datetime import datetime
from save_lead import save_lead

# Este script se integraría con webhooks de Telegram/WhatsApp
# Por ahora, vamos a usarlo como helper manual

def extract_lead_from_conversation(conversacion):
    """
    Extrae datos de lead de una conversación
    Busca patrones como:
    - Empresa: oftalmología, e-commerce, etc.
    - Servicio: WhatsApp, CRM, etc.
    - Empleados: número
    """
    
    # Buscar nombre
    nombre = "Lead"
    apellido = "Orquesta"
    
    # Buscar empresa en el contexto
    empresa = "No especificada"
    servicio = "Consultoría"
    
    # Patrones a buscar en la conversación
    for linea in conversacion:
        texto = linea.lower()
        
        # Empresa
        if "empresa" in texto or "se dedica" in texto:
            # Siguiente línea probablemente tenga la respuesta
            empresa = linea
        
        # Servicio
        if "automatizar" in texto or "mejorar" in texto:
            if "whatsapp" in texto:
                servicio = "Automatización WhatsApp"
            elif "crm" in texto:
                servicio = "Automatización CRM"
            elif "ecommerce" in texto:
                servicio = "Consultoría E-commerce"
    
    return nombre, apellido, empresa, servicio

def manual_save_lead(nombre, apellido, empresa, servicio):
    """Guarda un lead manualmente"""
    return save_lead(nombre, apellido, empresa, servicio)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "save":
            # Uso: python auto_capture_leads.py save "Nombre" "Apellido" "Empresa" "Servicio"
            if len(sys.argv) >= 6:
                nombre = sys.argv[2]
                apellido = sys.argv[3]
                empresa = sys.argv[4]
                servicio = sys.argv[5]
                manual_save_lead(nombre, apellido, empresa, servicio)
        else:
            print("Comandos:")
            print("  python auto_capture_leads.py save <nombre> <apellido> <empresa> <servicio>")
