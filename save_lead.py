#!/usr/bin/env python3
"""
Save Lead to leads.json
Guarda un lead calificado automáticamente
Uso: python save_lead.py "Nombre" "Apellido" "Empresa" "Servicio"
"""

import json
import sys
import os
from datetime import datetime

LEADS_FILE = os.path.expanduser("~/.openclaw/workspace/leads.json")

def save_lead(nombre, apellido, empresa, servicio):
    """Guarda un lead en leads.json"""
    
    lead = {
        "nombre": nombre,
        "apellido": apellido,
        "empresa": empresa,
        "servicio": servicio,
        "fecha": datetime.now().isoformat(),
        "processed": False
    }
    
    # Leer leads existentes
    try:
        with open(LEADS_FILE, "r") as f:
            leads = json.load(f)
            if not isinstance(leads, list):
                leads = []
    except:
        leads = []
    
    # Agregar el nuevo lead
    leads.append(lead)
    
    # Guardar
    try:
        with open(LEADS_FILE, "w") as f:
            json.dump(leads, f, indent=2)
        print(f"✅ Lead guardado: {nombre} {apellido} ({empresa})")
        return True
    except Exception as e:
        print(f"❌ Error guardando: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python save_lead.py <nombre> <apellido> <empresa> <servicio>")
        sys.exit(1)
    
    nombre = sys.argv[1]
    apellido = sys.argv[2]
    empresa = sys.argv[3]
    servicio = sys.argv[4]
    
    save_lead(nombre, apellido, empresa, servicio)
