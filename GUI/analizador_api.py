import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai  # Usamos la librería moderna oficial

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================================================
# 🔑 CONFIGURACIÓN DEL CLIENTE GOOGLE GENAI
# ==============================================================================
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    logger.warning("NO SE ENCONTRÓ LA GOOGLE_API_KEY EN EL ARCHIVO .ENV")

try:
    # Instanciamos el cliente con la nueva sintaxis
    client = genai.Client(api_key=api_key)
except Exception as e:
    logger.error(f"Error al configurar el cliente de Google: {e}")
    client = None

# ==============================================================================
# 📝 PROMPT DEL SISTEMA
# ==============================================================================
PROMPT_SYSTEM_FINAL = """
Eres CodeCoach, un tutor de programación C++ experto y amigable.
Tu objetivo es ayudar al estudiante a encontrar sus errores sin darle la solución copiada.

INSTRUCCIONES:
1. Analiza el código y el error de consola.
2. Explica el error en lenguaje sencillo.
3. Si el código no compila, di exactamente qué línea falla.
4. Si el código funciona, analiza su complejidad Big O.
5. Sé breve, usa saltos de línea y NO uses emojis en exceso.
6. Háblale de "tú" al estudiante.
"""

# ==============================================================================
# SERVIDOR FASTAPI
# ==============================================================================
app = FastAPI()

# Modelo de datos corregido (Ahora incluye instrucciones_especificas)
class SolucionEntrada(BaseModel):
    codigo_usuario: str
    resultados_evaluacion: str
    problema_enunciado: str
    lenguaje: str = "C++"
    instrucciones_especificas: str = ""  #  Campo agregado para evitar errores

@app.get("/health")
async def health():
    """Endpoint para verificar si el servidor está vivo"""
    if client:
        return {"status": "ready", "model": "gemini-1.5-flash"}
    return {"status": "error", "message": "Cliente AI no configurado"}

@app.post("/analyze_solution")
async def analyze_solution(data: SolucionEntrada):
    if not client:
        return {
            "status": "error",
            "message": "La API Key no está configurada. Revisa tu archivo .env"
        }

    try:
        # Construcción del prompt
        mensaje_completo = f"""{PROMPT_SYSTEM_FINAL}

--- INSTRUCCIONES ESPECÍFICAS ---
{data.instrucciones_especificas}

--- CONTEXTO ---
Problema: {data.problema_enunciado}

--- CÓDIGO DEL ESTUDIANTE ---
```cpp
{data.codigo_usuario}
--- RESULTADO DE LA EJECUCIÓN --- {data.resultados_evaluacion}

Por favor, dame tu análisis siguiendo las instrucciones:"""

        logger.info(" Enviando solicitud a Gemini 1.5 Flash...")

        # Llamada a la API usando la nueva sintaxis (v1.0+)
        # 'gemini-1.5-flash' es rápido y gratuito en el tier free
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=mensaje_completo
        )

        logger.info("respuesta recibida de Gemini")


        return {
            "status": "success",
            "feedback_completo": response.text
        }

    except Exception as e:
        logger.error(f" Error en Gemini: {e}")
        return {
            "status": "error",
            "message": str(e),
            "feedback_completo": f"Error conectando con Gemini: {str(e)}"
        }
