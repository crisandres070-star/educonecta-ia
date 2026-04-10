from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "SECRET_KEY",
    "GEMINI_API_KEY",
    "SENDGRID_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "FRONTEND_URL",
]

PLACEHOLDER_VALUES = {
    "tu_api_key_aqui",
    "tu_sid_aqui",
    "tu_token_aqui",
    "tu_secret_key",
    "tu_api_key",
    "tu_sid",
    "tu_token",
}


def _is_placeholder(key: str, value: str) -> bool:
    if value.strip() == "":
        return True
    if value in PLACEHOLDER_VALUES:
        return True
    if key == "GEMINI_API_KEY" and value.startswith("tu_"):
        return True
    if key == "SENDGRID_API_KEY" and value.startswith("tu_"):
        return True
    if key == "TWILIO_ACCOUNT_SID" and value.startswith("tu_"):
        return True
    if key == "TWILIO_AUTH_TOKEN" and value.startswith("tu_"):
        return True
    return False


def main() -> int:
    load_dotenv()

    missing = [key for key in REQUIRED_ENV_VARS if not os.getenv(key)]
    if missing:
        print("Variables faltantes en .env:")
        for key in missing:
            print(f"- {key}")
        print("Sugerencia: copia .env.example a .env y completa los valores.")
        return 1

    placeholders = [key for key in REQUIRED_ENV_VARS if _is_placeholder(key, os.getenv(key, ""))]
    if placeholders:
        print("Variables .env aun en valor de ejemplo:")
        for key in placeholders:
            print(f"- {key}")
        print("Sugerencia: reemplaza los placeholders por credenciales reales.")
        return 1

    database_url = os.getenv("DATABASE_URL", "")
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Conexion exitosa. Listo para continuar.")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"Error de conexion: {exc}")
        print(
            "Sugerencia: verifica que PostgreSQL este iniciado, el puerto 5432 este libre, "
            "y que DATABASE_URL tenga usuario/contrasena/base correctos."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
