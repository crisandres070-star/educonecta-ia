import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key cargada: {api_key[:10]}..." if api_key else "ERROR: GEMINI_API_KEY no encontrada en .env")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content("Responde solo: Gemini funcionando correctamente")
    print("Gemini conectado correctamente")
    print(f"Respuesta: {response.text}")
except Exception as e:
    print(f"Error exacto: {type(e).__name__}: {str(e)}")
