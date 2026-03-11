# 🚀 Guía de Setup - Orquesta en AWS EC2 + RDS

## Paso 1: Crear RDS (PostgreSQL)

1. **Abre AWS Console** → RDS → Crear base de datos
2. **Selecciona PostgreSQL** (versión 14+)
3. **Configuración:**
   - Nombre DB: `orquesta`
   - Usuario: `postgres`
   - Contraseña: Anotar (la usarás después)
   - Storage: 20 GB (libre tier)
   - Acceso público: **SÍ** (temporalmente para testing)

4. **Crea y anota el endpoint** (ej: `orquesta.xxxxx.us-east-1.rds.amazonaws.com`)

---

## Paso 2: Crear EC2 (Servidor)

1. **Abre AWS Console** → EC2 → Lanzar instancia
2. **Configuración:**
   - AMI: **Ubuntu 20.04 LTS** (free tier)
   - Tipo: `t2.micro` (free tier)
   - Storage: 8 GB (default)
   - Security Group: Permitir puertos 22 (SSH), 80 (HTTP), 443 (HTTPS)

3. **Crea key pair** (guarda el .pem)
4. **Lanza instancia** y anota la **IP pública**

---

## Paso 3: Conectar a EC2 por SSH

```bash
# En tu terminal local
chmod 400 ~/Downloads/tu-key.pem
ssh -i ~/Downloads/tu-key.pem ubuntu@TU_IP_PUBLICA
```

---

## Paso 4: Instalar en EC2

Una vez dentro del servidor:

```bash
# Actualizar
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git

# Crear directorio
mkdir -p ~/orquesta
cd ~/orquesta

# Virtual env
python3 -m venv venv
source venv/bin/activate

# Dependencias
pip install requests psycopg2-binary python-dotenv
```

---

## Paso 5: Copiar archivos

En tu máquina local:

```bash
# Copiar archivo de app
scp -i ~/Downloads/tu-key.pem ~/..../app_production.py ubuntu@TU_IP:/home/ubuntu/orquesta/

# Copiar HTML
scp -i ~/Downloads/tu-key.pem ~/..../formulario.html ubuntu@TU_IP:/home/ubuntu/orquesta/
scp -i ~/Downloads/tu-key.pem ~/..../dashboard.html ubuntu@TU_IP:/home/ubuntu/orquesta/
```

---

## Paso 6: Configurar .env

En EC2:

```bash
cat > ~/orquesta/.env << EOF
DB_HOST=<RDS_ENDPOINT>
DB_NAME=orquesta
DB_USER=postgres
DB_PASSWORD=<TU_PASSWORD>
DB_PORT=5432

HUBSPOT_TOKEN=pat-na1-aa8b8d13-2e8a-407b-ae2e-df9e6963ac69
PORTAL_ID=51191100
CALENDLY_LINK=https://calendly.com/ignacio-orquesta-ai/30min
EOF
```

---

## Paso 7: Iniciar servidor

```bash
cd ~/orquesta
source venv/bin/activate
python3 app_production.py
```

Debería ver:
```
🚀 ORQUESTA - SERVIDOR DE PRODUCCIÓN
   URL: http://localhost:8000
   Dashboard: http://localhost:8000/dashboard
   BD: TU_RDS_ENDPOINT:5432/orquesta
```

---

## Paso 8: Exponer públicamente (Nginx)

Instalar Nginx:

```bash
sudo apt-get install -y nginx
```

Crear config:

```bash
sudo nano /etc/nginx/sites-available/default
```

Reemplaza con:

```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Reiniciar Nginx:

```bash
sudo systemctl restart nginx
```

---

## Paso 9: Acceder

Abre en tu navegador:

```
http://TU_IP_PUBLICA
```

Deberías ver el **formulario de Orquesta**.

---

## Paso 10: (Opcional) Dominio + SSL

1. Compra dominio (ej: en Route53 o Namecheap)
2. Apunta a la IP pública de EC2
3. Instala certbot para SSL:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com
```

---

## ✅ ¡LISTO!

Tu sistema está en producción con:
- ✅ Formulario público
- ✅ Dashboard con datos históricos en PostgreSQL
- ✅ Sincronización automática con HubSpot
- ✅ Escalable sin limitaciones

---

## 💰 Costos mensuales:

- **EC2 t2.micro:** ~$8-10
- **RDS PostgreSQL small:** ~$15
- **Total:** ~$23-25/mes

(Primer año: gratis con free tier de AWS)
