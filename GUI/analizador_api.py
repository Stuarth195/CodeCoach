# analizador_api.py - REEMPLAZAR el archivo completo con:

# FIX PARA CARGA RÁPIDA
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from fastapi import FastAPI
from pydantic import BaseModel
import logging
import time
import asyncio

"""
API DE ANÁLISIS DE CÓDIGO - VERSIÓN LIGERA
Usa análisis basado en reglas para respuesta inmediata
"""

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define la estructura de datos de entrada
class SolucionEntrada(BaseModel):
    codigo_usuario: str
    resultados_evaluacion: str
    problema_enunciado: str
    lenguaje: str = "C++"
    instrucciones_especificas: str = ""


# Inicializar FastAPI
app = FastAPI(
    title="Analizador de Soluciones CodeCoach - Fast",
    description="API para análisis rápido de código",
    version="3.0.0"
)


def analizar_codigo_rapido(codigo: str, resultados: str) -> str:
    """Análisis rápido basado en reglas - SIN MODELOS PESADOS"""

    # Análisis de complejidad básico
    complejidad = "O(n)"
    if "for" in codigo and "for" in codigo:
        complejidad = "O(n²)"
    elif "while" in codigo and "for" not in codigo:
        complejidad = "O(n)"
    elif "recursion" in codigo.lower() or "recursive" in codigo.lower():
        complejidad = "O(2^n)"
    else:
        complejidad = "O(1)"

    # Detección de patrones comunes
    sugerencias = []

    if "cin >>" in codigo and "using namespace std" not in codigo:
        sugerencias.append("🔍 Agrega: #include <iostream> y using namespace std;")

    if "vector" in codigo and "#include <vector>" not in codigo:
        sugerencias.append("🔍 Incluye: #include <vector>")

    if "main()" in codigo and "return 0" not in codigo:
        sugerencias.append("🔍 Agrega 'return 0;' al final de main()")

    # Análisis de resultados
    if "error" in resultados.lower():
        sugerencias.append("⚠️  Tu código tiene errores de compilación")
    elif "passed" in resultados.lower() and "failed" not in resultados.lower():
        sugerencias.append("✅ ¡Excelente! Tu código pasa todas las pruebas")
    else:
        sugerencias.append("🔧 Revisa los casos de prueba fallidos")

    # Construir respuesta
    respuesta = f"""
🎯 **ANÁLISIS RÁPIDO**

📊 **Complejidad estimada:** {complejidad}

💡 **Sugerencias:**
{chr(10).join(['• ' + s for s in sugerencias])}

🚀 **Siguientes pasos:**
• Verifica que tu solución sea óptima
• Prueba con inputs grandes
• Considera casos edge
"""
    return respuesta


# Endpoints de la API
@app.get("/")
async def root():
    return {
        "message": "API de Análisis Rápido - Activa",
        "status": "ready",
        "version": "3.0.0"
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificar estado del servidor"""
    return {
        "status": "ready",
        "timestamp": time.time(),
        "model": "fast-analyzer"
    }


@app.post("/analyze_solution")
async def analyze_solution(data: SolucionEntrada):
    """
    Analiza código C++ usando reglas rápidas
    """
    try:
        inicio = time.time()

        # Validar datos de entrada
        if not data.codigo_usuario.strip():
            return {
                "status": "error",
                "message": "El código está vacío",
                "feedback_completo": "Por favor, escribe algún código antes de solicitar análisis."
            }

        logger.info(f"📥 Análisis rápido - Código: {len(data.codigo_usuario)} chars")

        # Análisis rápido
        feedback = analizar_codigo_rapido(data.codigo_usuario, data.resultados_evaluacion)

        tiempo_procesamiento = time.time() - inicio

        logger.info(f"✅ Análisis completado en {tiempo_procesamiento:.2f}s")

        return {
            "status": "success",
            "message": "Análisis rápido completado",
            "feedback_completo": feedback,
            "tiempo_procesamiento": f"{tiempo_procesamiento:.2f}s"
        }

    except Exception as e:
        logger.error(f"💥 Error en analyze_solution: {e}")
        return {
            "status": "error",
            "message": f"Error interno: {str(e)}",
            "feedback_completo": "❌ Error procesando tu solicitud. Intenta nuevamente."
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")