#!/bin/bash
# guardar_lead.sh - Script para guardar leads automáticamente

NOMBRE="${1:-Lead}"
APELLIDO="${2:-Orquesta}"
EMPRESA="${3:-No especificada}"
SERVICIO="${4:-Consultoría}"

python3 ~/.openclaw/workspace/save_lead.py "$NOMBRE" "$APELLIDO" "$EMPRESA" "$SERVICIO"
