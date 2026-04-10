# Setup PostgreSQL en Windows (sin Docker)

## 1) Descargar e instalar PostgreSQL

1. Entra al sitio oficial:
   https://www.postgresql.org/download/windows/
2. Haz clic en el instalador de EDB para Windows.
3. Durante la instalacion:
   - Deja el usuario por defecto: `postgres`
   - Define la contrasena: `postgres`
   - Puerto: `5432`
   - Locale por defecto
4. Finaliza la instalacion.

## 2) Verificar servicio PostgreSQL

1. Abre `services.msc`.
2. Busca el servicio PostgreSQL (ejemplo: `postgresql-x64-16`).
3. Verifica que este en estado `Running`.

## 3) Configurar usuario `postgres` con contrasena `postgres`

Si en la instalacion usaste otra clave, cambiala desde SQL Shell (`psql`):

```sql
ALTER USER postgres WITH PASSWORD 'postgres';
```

## 4) Crear la base de datos `educonecta`

1. Abre **SQL Shell (psql)**.
2. Ingresa estos valores cuando los pida:
   - Server: `localhost`
   - Database: `postgres`
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres`
3. Ejecuta:

```sql
CREATE DATABASE educonecta;
```

4. Verifica:

```sql
\l
```

Debe aparecer `educonecta` en la lista.

## 5) Configurar variables en .env

Crea o actualiza `.env` en la raiz de `educonecta`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/educonecta
SECRET_KEY=supersecretkey123
GEMINI_API_KEY=tu_api_key_aqui
SENDGRID_API_KEY=tu_api_key_aqui
TWILIO_ACCOUNT_SID=tu_sid_aqui
TWILIO_AUTH_TOKEN=tu_token_aqui
FRONTEND_URL=http://localhost:3000
```

## 6) Verificar conexion desde Python

En la raiz del proyecto:

```powershell
python check_connection.py
```

Si todo esta bien, veras:

```text
Conexion exitosa. Listo para continuar.
```
