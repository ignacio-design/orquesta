#!/usr/bin/env python3
"""
Twilio WhatsApp Webhook Handler
Recibe mensajes de WhatsApp vía Twilio y guarda leads automáticamente
"""

import json
import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from save_lead import save_lead
from datetime import datetime

class TwilioWebhookHandler(BaseHTTPRequestHandler):
    
    # Almacenar conversaciones en memoria (chat_id → conversación)
    conversations = {}
    
    def do_POST(self):
        """Recibe mensajes de Twilio"""
        
        if self.path != "/twilio-webhook":
            self.send_response(404)
            self.end_headers()
            return
        
        # Leer el body (Twilio envía datos en formato URL-encoded, no JSON)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        # Parsear datos
        data = parse_qs(body)
        
        # Extraer los campos (parse_qs devuelve listas, así que tomar el primero)
        phone = data.get('From', [''])[0]  # Ej: "whatsapp:+34612345678"
        message_text = data.get('Body', [''])[0]  # El mensaje del usuario
        
        print(f"📩 Mensaje de {phone}: {message_text}")
        
        # Procesar
        self.process_message(phone, message_text)
        
        # Responder 200 OK a Twilio
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.end_headers()
        
        # Responder con XML de Twilio (vacío es ok)
        response = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        self.wfile.write(response.encode('utf-8'))
    
    def process_message(self, phone, text):
        """Procesa un mensaje de WhatsApp/Twilio"""
        
        # Usar el teléfono como identificador único de conversación
        chat_id = phone
        
        # Inicializar conversación si no existe
        if chat_id not in self.conversations:
            self.conversations[chat_id] = {
                "messages": [],
                "data": {},
                "created_at": datetime.now().isoformat()
            }
        
        # Agregar mensaje a la conversación
        self.conversations[chat_id]["messages"].append({
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"   Mensajes en conversación: {len(self.conversations[chat_id]['messages'])}")
        
        # Extraer datos del mensaje
        self.extract_lead_data(chat_id, text)
        
        # Verificar si se completó
        if self.is_lead_complete(chat_id):
            print(f"✅ Lead completado! Guardando...")
            self.save_lead_auto(chat_id)
    
    def extract_lead_data(self, chat_id, text):
        """Extrae datos de lead de los mensajes"""
        
        data = self.conversations[chat_id]["data"]
        text_lower = text.lower()
        
        print(f"   Extrayendo datos... empresa={data.get('empresa')}, servicio={data.get('servicio')}")
        
        # ✅ Detectar EMPRESA
        # El bot pregunta: "¿A qué se dedica tu empresa?"
        if not data.get("empresa"):
            empresa_patterns = [
                r'(?:se dedica(?:n)? a|empresa|somos?|trabajo(?:mos)? en|rubro)\s+([a-záéíóúñ\s\-]+)',
                r'(oftalmología|ecommerce|consultora|consultoría|agencia|tecnología|veterinaria|farmacia|construcción|educación|salud)',
            ]
            for pattern in empresa_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    empresa = match.group(1).strip()
                    # Limpiar
                    empresa = re.sub(r'[?.,!]', '', empresa)
                    data["empresa"] = empresa.title()
                    print(f"   ✓ Empresa detectada: {data['empresa']}")
                    break
        
        # ✅ Detectar SERVICIO
        # El bot pregunta: "¿Qué querés automatizar?"
        if not data.get("servicio"):
            service_patterns = [
                r'(?:automatizar|mejorar|querés?|quieren?|necesito?|hacer|implementar)\s+([a-záéíóúñ\s\-]+)',
                r'(whatsapp|crm|ecommerce|consultas|pedidos|reservas|facturación|inventario|rrhh)',
            ]
            for pattern in service_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    servicio = match.group(1).strip()
                    # Limpiar
                    servicio = re.sub(r'[?.,!]', '', servicio)
                    data["servicio"] = servicio.title()
                    print(f"   ✓ Servicio detectado: {data['servicio']}")
                    break
        
        # ✅ Detectar EMPLEADOS
        # El bot pregunta: "¿Cuántos empleados?"
        if not data.get("empleados"):
            # Buscar números
            numbers = re.findall(r'\d+', text)
            if numbers:
                data["empleados"] = int(numbers[0])
                print(f"   ✓ Empleados detectados: {data['empleados']}")
    
    def is_lead_complete(self, chat_id):
        """Verifica si la conversación fue completada (3 datos)"""
        
        data = self.conversations[chat_id]["data"]
        
        # Necesitamos estos 3 campos mínimo
        has_empresa = bool(data.get("empresa"))
        has_servicio = bool(data.get("servicio"))
        has_empleados = data.get("empleados") is not None
        
        complete = has_empresa and has_servicio and has_empleados
        
        if complete:
            print(f"   📊 Estado: empresa✓ servicio✓ empleados✓ → COMPLETO")
        else:
            print(f"   📊 Estado: empresa{'✓' if has_empresa else '✗'} servicio{'✓' if has_servicio else '✗'} empleados{'✓' if has_empleados else '✗'}")
        
        return complete
    
    def save_lead_auto(self, chat_id):
        """Automáticamente guarda el lead"""
        
        data = self.conversations[chat_id]["data"]
        
        # Preparar datos
        nombre = data.get("nombre", "Prospecto")  # Si no hay nombre, usar genérico
        apellido = "WhatsApp"  # O usar el número de teléfono
        empresa = data.get("empresa", "No especificada")
        servicio = data.get("servicio", "Consultoría")
        
        print(f"   💾 Guardando: {nombre} de {empresa}")
        
        try:
            # Guardar en leads.json
            resultado = save_lead(nombre, apellido, empresa, servicio)
            print(f"   ✅ Lead guardado exitosamente")
            
            # Marcar como guardado (para no duplicar)
            self.conversations[chat_id]["data"]["guardado"] = True
            
        except Exception as e:
            print(f"   ❌ Error al guardar: {e}")

def start_webhook_server(port=8001):
    """Inicia el servidor webhook de Twilio"""
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, TwilioWebhookHandler)
    
    print("=" * 60)
    print("🔗 WEBHOOK DE TWILIO/WHATSAPP ACTIVO")
    print("=" * 60)
    print(f"   Puerto: {port}")
    print(f"   URL pública: http://TU_IP:{port}/twilio-webhook")
    print(f"   (Necesitás exponer esto con ngrok o similar)")
    print()
    print("📋 Esperando mensajes de WhatsApp...")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Webhook detenido")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    start_webhook_server(port)
