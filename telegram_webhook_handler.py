#!/usr/bin/env python3
"""
Telegram Webhook Handler
Recibe mensajes de Telegram y automáticamente guarda leads completados
"""

import json
import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from save_lead import save_lead

class TelegramWebhookHandler(BaseHTTPRequestHandler):
    
    # Almacenar conversaciones en memoria
    conversations = {}
    
    def do_POST(self):
        """Recibe mensajes de Telegram"""
        
        if self.path != "/telegram-webhook":
            self.send_response(404)
            return
        
        # Leer el body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
        except:
            self.send_response(400)
            self.end_headers()
            return
        
        # Procesar mensaje
        self.process_message(data)
        
        # Responder OK a Telegram
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    
    def process_message(self, data):
        """Procesa un mensaje de Telegram"""
        
        # Extraer info
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user_id = message.get("from", {}).get("id")
        
        if not chat_id:
            return
        
        # Inicializar conversación si no existe
        if chat_id not in self.conversations:
            self.conversations[chat_id] = {
                "messages": [],
                "data": {}
            }
        
        # Agregar mensaje
        self.conversations[chat_id]["messages"].append({
            "text": text,
            "user_id": user_id
        })
        
        # Detectar respuestas del usuario
        self.extract_lead_data(chat_id, text)
        
        # Verificar si se completó la calificación
        if self.is_lead_complete(chat_id):
            self.save_lead_auto(chat_id)
    
    def extract_lead_data(self, chat_id, text):
        """Extrae datos de lead de los mensajes"""
        
        data = self.conversations[chat_id]["data"]
        text_lower = text.lower()
        
        # Detectar empresa
        if not data.get("empresa"):
            empresa_patterns = [
                r'(?:se dedica a|es|soy|trabajo en)\s+([a-záéíóú\s]+)',
                r'(oftalmología|ecommerce|consultora|agencia|tecnología|veterinaria|farmacia)',
            ]
            for pattern in empresa_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    data["empresa"] = match.group(1).strip()
                    break
        
        # Detectar servicio
        if not data.get("servicio"):
            if "whatsapp" in text_lower:
                data["servicio"] = "Automatización WhatsApp"
            elif "crm" in text_lower:
                data["servicio"] = "Automatización CRM"
            elif "ecommerce" in text_lower:
                data["servicio"] = "Consultoría E-commerce"
            elif "automatizar" in text_lower or "mejorar" in text_lower:
                data["servicio"] = text.strip()[:50]
        
        # Detectar empleados
        if not data.get("empleados"):
            employees_match = re.search(r'(\d+)', text)
            if employees_match:
                data["empleados"] = employees_match.group(1)
        
        # Detectar nombre
        if not data.get("nombre"):
            # Buscar en los primeros mensajes
            first_messages = " ".join([m["text"] for m in self.conversations[chat_id]["messages"][:3]])
            name_match = re.search(r'(?:hola|hi|soy|me llamo)\s+([A-Za-z]+)', first_messages.lower())
            if name_match:
                data["nombre"] = name_match.group(1).capitalize()
    
    def is_lead_complete(self, chat_id):
        """Verifica si la conversación fue completada"""
        
        data = self.conversations[chat_id]["data"]
        
        # Necesitamos empresa y servicio como mínimo
        return bool(data.get("empresa") and data.get("servicio"))
    
    def save_lead_auto(self, chat_id):
        """Automáticamente guarda el lead"""
        
        data = self.conversations[chat_id]["data"]
        
        nombre = data.get("nombre", "Lead")
        apellido = "Orquesta"
        empresa = data.get("empresa", "No especificada")
        servicio = data.get("servicio", "Consultoría")
        
        # Guardar
        save_lead(nombre, apellido, empresa, servicio)
        
        # Marcar como guardado (para no duplicar)
        self.conversations[chat_id]["data"]["guardado"] = True

def start_webhook_server(port=8000):
    """Inicia el servidor webhook"""
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, TelegramWebhookHandler)
    
    print(f"🔗 Webhook de Telegram escuchando en puerto {port}")
    print(f"URL: http://localhost:{port}/telegram-webhook")
    print("Esperando mensajes...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Webhook detenido")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_webhook_server(port)
