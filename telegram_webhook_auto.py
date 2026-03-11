#!/usr/bin/env python3
"""
Telegram Webhook - Auto-detección y guardado de leads
Detecta cuando se completan las 3 preguntas, guarda automáticamente
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
from datetime import datetime
from save_lead import save_lead

# Estado global de conversaciones
conversations = {}

class TelegramWebhookHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Sobrescribir logs para más claridad"""
        print(f"[{self.log_date_time_string()}] {format % args}", flush=True)
    
    def do_POST(self):
        """Recibe updates de Telegram"""
        
        if self.path != "/telegram-webhook":
            self.send_response(404)
            self.end_headers()
            return
        
        # Leer el body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except:
            self.send_response(400)
            self.end_headers()
            return
        
        # Extraer mensaje
        if 'message' not in data:
            self.send_response(200)
            self.end_headers()
            return
        
        msg = data['message']
        chat_id = msg['chat']['id']
        user_name = msg['from'].get('first_name', 'Usuario')
        text = msg.get('text', '').strip()
        
        print(f"\n📱 MENSAJE RECIBIDO")
        print(f"   Chat ID: {chat_id}")
        print(f"   Usuario: {user_name}")
        print(f"   Texto: {text}")
        
        # Procesar
        self.process_message(chat_id, user_name, text)
        
        # Responder 200 OK a Telegram
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')
    
    def process_message(self, chat_id, user_name, text):
        """Procesa un mensaje y detecta cuando está completo"""
        
        # Inicializar conversación si no existe
        if chat_id not in conversations:
            conversations[chat_id] = {
                "nombre": user_name,
                "empresa": None,
                "servicio": None,
                "empleados": None,
                "created_at": datetime.now().isoformat(),
                "guardado": False
            }
        
        conv = conversations[chat_id]
        
        # Extraer EMPRESA
        if not conv['empresa']:
            empresa_match = re.search(
                r'(?:se dedica(?:n)? a|empresa|somos?|trabajo(?:mos)? en|rubro)\s+([a-záéíóúñ\s\-]+)',
                text.lower()
            )
            if empresa_match or any(word in text.lower() for word in ['ecommerce', 'consultora', 'oftalmología', 'veterinaria', 'farmacia', 'construcción']):
                if empresa_match:
                    conv['empresa'] = empresa_match.group(1).strip().title()
                else:
                    # Si no tiene el patrón, buscar palabra directa
                    for word in ['ecommerce', 'consultora', 'oftalmología', 'veterinaria', 'farmacia', 'construcción', 'educación', 'salud', 'agencia', 'tecnología']:
                        if word in text.lower():
                            conv['empresa'] = word.title()
                            break
                
                if conv['empresa']:
                    print(f"   ✓ Empresa detectada: {conv['empresa']}")
        
        # Extraer SERVICIO
        if not conv['servicio']:
            servicio_match = re.search(
                r'(?:automatizar|mejorar|querés?|quieren?|necesito?|hacer|implementar)\s+([a-záéíóúñ\s\-]+)',
                text.lower()
            )
            if servicio_match or any(word in text.lower() for word in ['whatsapp', 'crm', 'facturación', 'pedidos', 'reservas']):
                if servicio_match:
                    conv['servicio'] = servicio_match.group(1).strip().title()
                else:
                    for word in ['whatsapp', 'crm', 'facturación', 'pedidos', 'reservas', 'inventario', 'rrhh', 'consultas']:
                        if word in text.lower():
                            conv['servicio'] = word.title()
                            break
                
                if conv['servicio']:
                    print(f"   ✓ Servicio detectado: {conv['servicio']}")
        
        # Extraer EMPLEADOS
        if conv['empleados'] is None:
            numeros = re.findall(r'\d+', text)
            if numeros:
                conv['empleados'] = int(numeros[0])
                print(f"   ✓ Empleados detectados: {conv['empleados']}")
        
        # Verificar si está completo
        is_complete = conv['empresa'] and conv['servicio'] and conv['empleados'] is not None
        
        print(f"   📊 Estado: empresa{'✓' if conv['empresa'] else '✗'} servicio{'✓' if conv['servicio'] else '✗'} empleados{'✓' if conv['empleados'] is not None else '✗'}")
        
        # SI ESTÁ COMPLETO Y NO GUARDADO → GUARDAR AUTOMÁTICAMENTE
        if is_complete and not conv['guardado']:
            print(f"   🎯 LEAD COMPLETADO - Guardando automáticamente...")
            self.save_lead_auto(chat_id, conv)
    
    def save_lead_auto(self, chat_id, conv):
        """Guarda el lead automáticamente"""
        
        try:
            # Usar nombre del usuario o genérico
            nombre = conv['nombre']
            apellido = f"Telegram_{chat_id}"  # Identificador único
            empresa = conv['empresa']
            servicio = conv['servicio']
            
            print(f"   💾 Guardando: {nombre} de {empresa}")
            
            # Guardar en leads.json
            save_lead(nombre, apellido, empresa, servicio)
            
            # Marcar como guardado
            conv['guardado'] = True
            
            print(f"   ✅ Lead guardado exitosamente")
            print(f"   🔄 HubSpot sincronizará en <1 minuto\n")
            
        except Exception as e:
            print(f"   ❌ Error al guardar: {e}\n")

def start_webhook_server(port=8002):
    """Inicia el servidor webhook de Telegram"""
    
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, TelegramWebhookHandler)
    
    print("=" * 60)
    print("🟢 TELEGRAM WEBHOOK AUTOMÁTICO ACTIVO")
    print("=" * 60)
    print(f"   Puerto: {port}")
    print(f"   Endpoint: http://localhost:{port}/telegram-webhook")
    print(f"   Estado: Escuchando mensajes de Telegram...")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Webhook detenido")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    start_webhook_server(port)
