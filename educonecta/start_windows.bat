@echo off
setlocal

cd /d "%~dp0"

echo [1/5] Verificando conexion a PostgreSQL...
python check_connection.py
if errorlevel 1 (
  echo Conexion no disponible. Revisa SETUP_WINDOWS.md.
  exit /b 1
)

echo [2/5] Ejecutando migraciones...
alembic upgrade head
if errorlevel 1 (
  echo Fallo alembic upgrade head.
  exit /b 1
)

echo [3/5] Cargando datos seed...
python seed.py
if errorlevel 1 (
  echo Fallo seed.py.
  exit /b 1
)

echo [4/5] Abriendo Swagger Docs...
start "" "http://localhost:8000/docs"

echo [5/5] Iniciando servidor FastAPI...
uvicorn app.main:app --reload
