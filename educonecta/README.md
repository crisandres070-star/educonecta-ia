# EduConecta IA

Plataforma SaaS para colegios chilenos que conecta profesores, apoderados y directivos con apoyo de IA.

## Stack

- Backend: FastAPI + Python 3.11+
- Base de datos: PostgreSQL + SQLAlchemy
- IA: Google Gemini (`gemini-1.5-flash`)
- Auth: JWT con roles (`profesor`, `apoderado`, `directivo`)
- Notificaciones: SendGrid (email) + Twilio (WhatsApp)

## Estructura

```text
educonecta/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── middleware/
├── tests/
├── .env.example
├── requirements.txt
├── README.md
└── docker-compose.yml
```

## Instalacion local

1. Crear y activar entorno virtual:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Crear archivo de entorno desde el ejemplo:

```bash
cp .env.example .env
```

En Windows PowerShell usa:

```powershell
Copy-Item .env.example .env
```

4. Levantar PostgreSQL con Docker:

```bash
docker compose up -d
```

5. Ejecutar API:

```bash
uvicorn app.main:app --reload
```

## Endpoints principales

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`

### Profesores

- `POST /profesor/notas`
- `POST /profesor/anotaciones`
- `POST /profesor/asistencia`
- `GET /profesor/mis-alumnos`
- `POST /profesor/alertas`

### Apoderados

- `GET /apoderado/mi-hijo/{alumno_id}`
- `GET /apoderado/notas/{alumno_id}`
- `GET /apoderado/alertas/{alumno_id}`
- `POST /apoderado/chat`
- `GET /apoderado/recomendaciones/{alumno_id}`

### Directivos

- `GET /directivo/dashboard`
- `GET /directivo/alertas`
- `GET /directivo/rendimiento`

## Variables de entorno

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/educonecta
SECRET_KEY=supersecretkey123
GEMINI_API_KEY=tu_api_key_aqui
SENDGRID_API_KEY=tu_api_key_aqui
TWILIO_ACCOUNT_SID=tu_sid_aqui
TWILIO_AUTH_TOKEN=tu_token_aqui
FRONTEND_URL=http://localhost:3000
```

## Notas

- Actualmente se crea el esquema SQL automáticamente en el startup de FastAPI con `Base.metadata.create_all`.
- Para producción se recomienda migrar a Alembic.
- El router de auth está completo y los routers de dominio ya están operativos para un MVP inicial.
