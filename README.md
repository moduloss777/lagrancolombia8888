# 📱 SMS Marketing API v2.0

Aplicación Flask optimizada para **Render** con integración completa de **TraffiLink API**.

## 🚀 Características

- ✅ **API REST** para envío de SMS
- ✅ **TraffiLink** integrado como principal
- ✅ **Dashboard** minimalista y funcional
- ✅ **Base de datos** SQLite persistente
- ✅ **5 dependencias** mínimas
- ✅ **Deploy en Render** en 30 segundos
- ✅ **Webhooks** para confirmación de entrega
- ✅ **Balance en tiempo real** de TraffiLink

## 📋 Requisitos

- Python 3.12+
- pip (gestor de paquetes)

## 🔧 Instalación Local

```bash
# 1. Clonar o descargar proyecto
cd GoleadorSmsMarketing-v2

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear archivo .env con credenciales
cp .env.example .env
# Editar .env y agregar credenciales de TraffiLink

# 4. Ejecutar aplicación
python app.py

# 5. Abrir en navegador
http://localhost:5000
```

## 🌐 Endpoints API

### Health & Balance
```
GET /                           → Dashboard
GET /api/health                 → Health check
GET /api/stats                  → Estadísticas
GET /api/balance                → Balance TraffiLink (EUR)
```

### SMS Operations
```
POST /api/sms/send
{
    "numero": "573001234567",
    "mensaje": "Hola test"
}
→ { id, status, traffilink_id }

POST /api/sms/send-batch
{
    "sms": [
        { "numero": "57...", "mensaje": "..." },
        { "numero": "57...", "mensaje": "..." }
    ]
}
→ [{ id, status, traffilink_id }, ...]

GET /api/sms/status/{id}
→ { id, numero, status, traffilink_id, error }
```

### Webhooks
```
POST /webhook/traffilink
{
    "id": "traffilink_id",
    "deliverystatus": "1",
    "timestamp": "2026-02-23 20:00:00"
}
```

## 📊 Estructura

```
GoleadorSmsMarketing-v2/
├── app.py                    # Flask app (200 líneas)
├── traffilink_api.py        # TraffiLink integration (150 líneas)
├── database.py              # SQLite manager (100 líneas)
├── config.py                # Configuración (40 líneas)
├── requirements.txt         # 5 dependencias
├── runtime.txt              # Python 3.12
├── Procfile                 # Para Render
├── .env.example             # Template
├── .gitignore               # Git ignore
├── README.md                # Este archivo
└── templates/
    └── index.html           # Dashboard
```

## 🔐 Variables de Entorno

```bash
TRAFFILINK_ACCOUNT=0152C274
TRAFFILINK_PASSWORD=G2o0jRnm
TRAFFILINK_URL=http://47.236.91.242:20003
DATABASE_URL=sms_marketing.db
PORT=5000
DEBUG=False
```

## 🚀 Deploy en Render

### Paso 1: Crear repositorio GitHub
```bash
# En tu PC, sube el proyecto a GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tusuario/GoleadorSmsMarketing-v2
git push -u origin main
```

### Paso 2: Conectar a Render
1. Ve a https://render.com
2. Haz clic en "New +" → "Web Service"
3. Conecta tu repositorio GitHub
4. Configura:
   - **Name**: goleador-sms-marketing
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

### Paso 3: Agregar variables de entorno
En Render → Environment:
```
TRAFFILINK_ACCOUNT = 0152C274
TRAFFILINK_PASSWORD = G2o0jRnm
TRAFFILINK_URL = http://47.236.91.242:20003
AMBIENTE = produccion
DEBUG = False
PORT = 5000
```

### Paso 4: Deploy
Haz clic en "Deploy" y espera a "Your service is live"

## 📈 Performance

| Métrica | Valor |
|---------|-------|
| Build time | 30 seg |
| Memory | 80 MB |
| Python | 3.12 |
| Dependencias | 5 |
| Líneas de código | ~800 |

## 🧪 Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Enviar SMS
curl -X POST http://localhost:5000/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{"numero":"573001234567","mensaje":"Test"}'

# Consultar balance
curl http://localhost:5000/api/balance

# Estadísticas
curl http://localhost:5000/api/stats
```

## 📞 Soporte

Para problemas:
1. Revisar logs: `tail -f app.log`
2. Verificar variables de entorno
3. Contactar a TraffiLink en https://my.traffilink.com

## 📄 Licencia

MIT License - Usa libremente

---

**SMS Marketing API v2.0** | Optimizado para Render | Desarrollado por GoleadorSmsMarketing
