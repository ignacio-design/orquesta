#!/usr/bin/env python3
"""
Orquesta - App Production (con PostgreSQL)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Conexión a PostgreSQL
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'orquesta')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_PORT = os.getenv('DB_PORT', '5432')

def get_db_connection():
    """Conecta a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Error conectando BD: {e}")
        return None

def init_db():
    """Crea tabla de leads si no existe"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                empresa VARCHAR(255),
                servicio TEXT,
                empleados INTEGER,
                email_sent BOOLEAN DEFAULT FALSE,
                status VARCHAR(50) DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        print("✅ Base de datos inicializada")
        return True
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        return False
    finally:
        conn.close()

class AppHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Sirve páginas HTML"""
        if self.path == '/':
            self.serve_html('formulario.html')
        elif self.path == '/dashboard':
            self.serve_html('dashboard.html')
        elif self.path == '/api/leads':
            self.get_leads()
        else:
            self.send_response(404)
            self.end_headers()
    
    def serve_html(self, filename):
        """Sirve archivo HTML"""
        try:
            file_path = os.path.expanduser(f'~/.openclaw/workspace/{filename}')
            with open(file_path, 'r') as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f.read().encode('utf-8'))
        except:
            self.send_response(404)
            self.end_headers()
    
    def get_leads(self):
        """Retorna leads en JSON"""
        conn = get_db_connection()
        if not conn:
            self.send_error(500, "Error de base de datos")
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nombre, empresa, servicio, empleados, status, created_at 
                FROM leads 
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            leads = []
            for row in rows:
                leads.append({
                    'nombre': row[0],
                    'empresa': row[1],
                    'servicio': row[2],
                    'empleados': row[3],
                    'status': row[4],
                    'fecha': row[5].isoformat()
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'leads': leads}).encode('utf-8'))
            
            cursor.close()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_error(500)
        finally:
            conn.close()
    
    def do_POST(self):
        """Recibe formularios"""
        if self.path == '/api/contacto':
            self.handle_contact()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_contact(self):
        """Procesa nuevo contacto"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            
            nombre = data.get('nombre', '').strip()
            empresa = data.get('empresa', '').strip()
            servicio = data.get('servicio', '').strip()
            empleados = data.get('empleados', 0)
            
            if not nombre or not empresa or not servicio:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Datos incompletos'}).encode())
                return
            
            # Guardar en BD
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO leads (nombre, empresa, servicio, empleados)
                    VALUES (%s, %s, %s, %s)
                """, (nombre, empresa, servicio, empleados))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"✅ Lead guardado: {nombre} - {empresa}")
            
            # Respuesta exitosa
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
            
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'JSON inválido'}).encode())
    
    def do_OPTIONS(self):
        """CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Logs limpios"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def start_server(port=8000):
    """Inicia servidor"""
    init_db()
    
    server = HTTPServer(('0.0.0.0', port), AppHandler)
    print("=" * 60)
    print("🚀 ORQUESTA - SERVIDOR DE PRODUCCIÓN")
    print("=" * 60)
    print(f"   URL: http://localhost:{port}")
    print(f"   Dashboard: http://localhost:{port}/dashboard")
    print(f"   BD: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Servidor detenido")

if __name__ == "__main__":
    start_server(8000)
