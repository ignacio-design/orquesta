#!/usr/bin/env python3
"""
Simple Twilio WhatsApp Webhook
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import json
import sys

class WebhookHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Sobrescribir logs"""
        print(f"[{self.log_date_time_string()}] {format % args}", flush=True)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        # Log del mensaje recibido
        print(f"\n📩 WEBHOOK RECIBIDO")
        print(f"   Body: {body[:200]}")
        
        # Parsear datos
        data = parse_qs(body)
        phone = data.get('From', [''])[0]
        message = data.get('Body', [''])[0]
        
        print(f"   📱 Desde: {phone}")
        print(f"   💬 Mensaje: {message}")
        
        # Responder 200 OK
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.end_headers()
        response = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        self.wfile.write(response.encode('utf-8'))
        
        print(f"   ✅ Respuesta enviada\n")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
    
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"🟢 Webhook activo en puerto {port}")
    print(f"   URL: http://localhost:{port}/")
    print(f"   Esperando mensajes...\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Webhook detenido")
