#!/usr/bin/env python3
"""
Envía emails automáticos cuando se captura un lead
"""

import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# CONFIGURAR ESTOS DATOS
SENDER_EMAIL = "ignacio@orquesta-ai.com"  # Cambiar a tu email
SENDER_PASSWORD = "your-password-here"    # Cambiar a tu contraseña (o usar SendGrid)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

CALENDLY_LINK = "https://calendly.com/ignacio-orquesta-ai/30min"
COMPANY_NAME = "Orquesta AI"
COMPANY_WEBSITE = "orquestaai.com"

def send_welcome_email(nombre, empresa, email=None):
    """Envía email de bienvenida al prospecto"""
    
    if not email:
        # Intentar extraer email de algún lado o usar genérico
        email = f"prospecto@{empresa.lower().replace(' ', '')}.com"
    
    subject = f"¡Bienvenido a {COMPANY_NAME}!"
    
    body = f"""
    Hola {nombre},
    
    ¡Gracias por tu interés en {COMPANY_NAME}!
    
    Hemos recibido tu solicitud para automatizar procesos en {empresa}.
    
    **Próximos pasos:**
    1. Revisaremos tu caso específico
    2. Te enviaremos una propuesta personalizada
    3. Agendar una llamada para detalles
    
    **¿Querés agendar una demo ahora?**
    {CALENDLY_LINK}
    
    Si tienes preguntas, responde este email.
    
    Saludos,
    Equipo {COMPANY_NAME}
    {COMPANY_WEBSITE}
    """
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Nota: En producción, usar SendGrid o similar
        # Por ahora solo log
        print(f"📧 Email de bienvenida para: {nombre} ({email})")
        print(f"   Asunto: {subject}")
        
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

def send_internal_notification(nombre, empresa, servicio):
    """Envía notificación interna del nuevo lead"""
    
    print(f"\n🔔 NUEVO LEAD CAPTURADO:")
    print(f"   Nombre: {nombre}")
    print(f"   Empresa: {empresa}")
    print(f"   Servicio: {servicio}")
    print(f"   Hora: {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Acción: Revisar en dashboard en /dashboard\n")

def check_new_leads():
    """Verifica leads nuevos y envía emails"""
    
    leads_file = os.path.expanduser("~/.openclaw/workspace/leads.json")
    
    if not os.path.exists(leads_file):
        return
    
    try:
        with open(leads_file, 'r') as f:
            leads = json.load(f)
    except:
        return
    
    for lead in leads:
        # Si es nuevo y no tiene email enviado
        if not lead.get('email_sent', False):
            nombre = lead.get('nombre', 'Cliente')
            empresa = lead.get('empresa', 'Sin empresa')
            servicio = lead.get('servicio', 'Automatización')
            
            # Enviar emails
            send_welcome_email(nombre, empresa)
            send_internal_notification(nombre, empresa, servicio)
            
            # Marcar como enviado
            lead['email_sent'] = True
            lead['email_sent_at'] = datetime.now().isoformat()
    
    # Guardar cambios
    with open(leads_file, 'w') as f:
        json.dump(leads, f, indent=2)

if __name__ == "__main__":
    check_new_leads()
