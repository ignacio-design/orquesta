#!/usr/bin/env python3
"""
Servidor web para formulario - Conecta a HubSpot
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import os
from datetime import datetime
from save_lead import save_lead

class FormHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Sirve formulario o dashboard"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with open(os.path.expanduser('~/.openclaw/workspace/formulario.html'), 'r') as f:
                self.wfile.write(f.read().encode('utf-8'))
        
        elif self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with open(os.path.expanduser('~/.openclaw/workspace/dashboard.html'), 'r') as f:
                self.wfile.write(f.read().encode('utf-8'))
        
        elif self.path == '/api/leads':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            leads_file = os.path.expanduser('~/.openclaw/workspace/leads.json')
            try:
                with open(leads_file, 'r') as f:
                    leads_data = json.load(f)
                
                # Agregar estado a cada lead
                for lead in leads_data:
                    if 'status' not in lead:
                        lead['status'] = 'new' if not lead.get('processed') else 'qualified'
                
                self.wfile.write(json.dumps({"leads": leads_data}).encode('utf-8'))
            except:
                self.wfile.write(json.dumps({"leads": []}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Recibe datos del formulario"""
        if self.path == '/api/contacto':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                
                nombre = data.get('nombre', 'Cliente').strip()
                empresa = data.get('empresa', 'No especificada').strip()
                servicio = data.get('servicio', 'Automatización').strip()
                empleados = data.get('empleados', 0)
                
                # Validar
                if not nombre or not empresa or not servicio:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Datos incompletos"}).encode())
                    return
                
                # Guardar en leads.json
                try:
                    save_lead(nombre, "Formulario", empresa, servicio)
                    print(f"✅ Lead guardado: {nombre} - {empresa}")
                except Exception as e:
                    print(f"❌ Error guardando: {e}")
                
                # Respuesta exitosa
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "ok",
                    "mensaje": "Consulta recibida"
                }).encode())
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "JSON inválido"}).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint no encontrado"}).encode())
    
    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Logs más limpios"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def start_server(port=8000):
    """Inicia servidor"""
    server = HTTPServer(('0.0.0.0', port), FormHandler)
    print("=" * 60)
    print("🌐 SERVIDOR DE FORMULARIO ACTIVO")
    print("=" * 60)
    print(f"   URL: http://localhost:{port}")
    print(f"   Endpoint: /api/contacto")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Servidor detenido")

if __name__ == "__main__":
    start_server(8000)
