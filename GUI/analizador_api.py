# analizador_api.py - VERSIÓN MEJORADA
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from fastapi import FastAPI
from pydantic import BaseModel
import logging
import time
import re
from typing import List, Dict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SolucionEntrada(BaseModel):
    codigo_usuario: str
    resultados_evaluacion: str
    problema_enunciado: str
    lenguaje: str = "C++"
    instrucciones_especificas: str = ""


app = FastAPI(
    title="Analizador de Soluciones CodeCoach - IA",
    description="API para análisis de complejidad y pistas inteligentes",
    version="4.0.0"
)


class AnalizadorComplejidad:
    """Analiza la complejidad algorítmica del código C++"""

    @staticmethod
    def analizar_complejidad(codigo: str) -> str:
        """Analiza la complejidad algorítmica basado en patrones del código"""

        # Limpiar comentarios
        codigo_limpio = re.sub(r'//.*$', '', codigo, flags=re.MULTILINE)
        codigo_limpio = re.sub(r'/\*.*?\*/', '', codigo_limpio, flags=re.DOTALL)

        # Detectar patrones de complejidad
        lineas = codigo_limpio.split('\n')
        complejidad = "O(1)"

        # Buscar bucles anidados
        bucles_anidados = 0
        nivel_anidamiento = 0
        max_anidamiento = 0

        for linea in lineas:
            linea = linea.strip()

            # Detectar inicio de bucle
            if re.search(r'\b(for|while)\s*\(', linea):
                nivel_anidamiento += 1
                max_anidamiento = max(max_anidamiento, nivel_anidamiento)
                if nivel_anidamiento == 2:
                    bucles_anidados += 1

            # Detectar fin de bloque
            if re.search(r'^\s*\}', linea) or re.search(r'\}\s*;?\s*$', linea):
                nivel_anidamiento = max(0, nivel_anidamiento - 1)

        # Determinar complejidad basada en patrones
        if max_anidamiento >= 3:
            complejidad = "O(n³)"
        elif bucles_anidados >= 1:
            complejidad = "O(n²)"
        elif max_anidamiento == 1:
            # Buscar si hay llamadas recursivas
            if re.search(r'\b' + re.escape(AnalizadorComplejidad._extraer_nombre_funcion(codigo)) + r'\s*\(', codigo):
                complejidad = "O(2^n)"  # Posible recursión exponencial
            else:
                complejidad = "O(n)"
        else:
            complejidad = "O(1)"

        # Verificar recursión más específicamente
        if AnalizadorComplejidad._detectar_recursion(codigo):
            if AnalizadorComplejidad._es_recursion_fibonacci(codigo):
                complejidad = "O(2^n)"
            else:
                complejidad = "O(n)"  # Recursión lineal

        return complejidad

    @staticmethod
    def _extraer_nombre_funcion(codigo: str) -> str:
        """Extrae el nombre de la función principal"""
        match = re.search(r'(?:bool|int|double|string|void|vector<\w+>)\s+(\w+)\s*\(', codigo)
        return match.group(1) if match else "main"

    @staticmethod
    def _detectar_recursion(codigo: str) -> bool:
        """Detecta si hay llamadas recursivas"""
        nombre_funcion = AnalizadorComplejidad._extraer_nombre_funcion(codigo)
        patron_recursion = r'\b' + re.escape(nombre_funcion) + r'\s*\('
        return bool(re.search(patron_recursion, codigo))

    @staticmethod
    def _es_recursion_fibonacci(codigo: str) -> bool:
        """Detecta patrones de recursión tipo Fibonacci"""
        return bool(re.search(r'return\s+\w+\s*\(\s*\w+\s*-\s*1\s*\)\s*\+\s*\w+\s*\(\s*\w+\s*-\s*2\s*\)', codigo))


class GeneradorPistas:
    """Genera pistas inteligentes basadas en errores comunes"""

    @staticmethod
    def generar_pistas_compilacion(errores: str, codigo: str) -> List[str]:
        """Genera pistas para errores de compilación"""
        pistas = []

        if "expected" in errores and ";" in errores:
            pistas.append("• Revisa que todas las líneas terminen con punto y coma (;)")

        if "undefined" in errores or "was not declared" in errores:
            pistas.append("• Verifica que todas las variables estén declaradas antes de usarse")
            pistas.append("• ¿Incluiste todas las bibliotecas necesarias? (#include)")

        if "expected" in errores and ")" in errores:
            pistas.append("• Revisa los paréntesis en condiciones if/while/for")

        # Detectar bibliotecas faltantes
        if "vector" in codigo and "#include <vector>" not in codigo:
            pistas.append("• Para usar vector, necesitas: #include <vector>")

        if "string" in codigo and "#include <string>" not in codigo:
            pistas.append("• Para usar string, necesitas: #include <string>")

        if "list" in codigo and "#include <list>" not in codigo:
            pistas.append("• Para usar list, necesitas: #include <list>")

        if not pistas:
            pistas.extend([
                "• Revisa la sintaxis línea por línea",
                "• Verifica que los nombres de funciones y variables coincidan",
                "• Asegúrate de que todos los { } estén balanceados"
            ])

        return pistas[:3]

    @staticmethod
    def generar_pistas_runtime(errores: str, codigo: str) -> List[str]:
        """Genera pistas para errores de ejecución"""
        pistas = []

        if "Timeout" in errores or "timeout" in errores.lower():
            pistas.extend([
                "• Tu código podría tener un bucle infinito",
                "• Verifica las condiciones de salida en while/for",
                "• ¿Estás incrementando correctamente las variables de control?"
            ])
        elif "segmentation" in errores.lower() or "segmentación" in errores.lower():
            pistas.extend([
                "• Podría haber acceso a memoria no válida",
                "• Revisa los índices en arrays/vectores",
                "• Verifica que no accedes a posiciones fuera de los límites"
            ])
        else:
            pistas.extend([
                "• Podría haber división por cero",
                "• Revisa el manejo de memoria dinámica",
                "• Verifica condiciones límite y casos extremos"
            ])

        return pistas[:3]

    @staticmethod
    def generar_pistas_logica(codigo: str, resultados: str) -> List[str]:
        """Genera pistas para errores de lógica"""
        pistas = []

        # Análisis de patrones comunes de errores
        if "if" in codigo and "else" not in codigo:
            pistas.append("• ¿Consideraste todos los casos posibles? Tal vez falta un 'else'")

        if "for" in codigo or "while" in codigo:
            pistas.append("• Revisa las condiciones de tus bucles")
            pistas.append("• ¿Estás iterando el número correcto de veces?")

        if "vector" in codigo or "list" in codigo:
            pistas.extend([
                "• Verifica el manejo de elementos en el contenedor",
                "• ¿Consideraste el caso del contenedor vacío?",
                "• Revisa los índices al acceder a elementos"
            ])

        if "return" not in codigo:
            pistas.append("• ¿Estás retornando el valor en todas las rutas posibles?")

        # Pistas generales de lógica
        pistas.extend([
            "• Prueba tu código con los ejemplos manualmente",
            "• Considera casos extremos (0, vacío, negativo, máximo)",
            "• Revisa los tipos de datos de entrada y salida"
        ])

        return pistas[:4]


def analizar_codigo_inteligente(codigo: str, resultados: str) -> str:
    """Análisis inteligente que combina complejidad y pistas"""

    # Detectar tipo de problema
    tiene_error_compilacion = any(
        term in resultados.lower() for term in ["compile_error", "error de compilación", "compilation error"])
    tiene_error_runtime = any(term in resultados.lower() for term in ["runtime_error", "timeout", "segmentation"])
    tiene_pruebas_fallidas = any(term in resultados.lower() for term in ["failed", "fallidas", "incorrecto"])
    es_exitoso = "success" in resultados.lower() and not tiene_pruebas_fallidas

    # Si es exitoso, dar análisis de complejidad
    if es_exitoso:
        complejidad = AnalizadorComplejidad.analizar_complejidad(codigo)

        feedback = f"""✅ **¡Excelente! Tu solución es correcta.**

📊 **Análisis de Complejidad:**
   - Complejidad temporal: {complejidad}
   - Eficiencia: {'Óptima' if complejidad in ['O(1)', 'O(log n)'] else 'Buena' if complejidad in ['O(n)', 'O(n log n)'] else 'Mejorable'}

💡 **Recomendaciones:**
   - {'Tu solución es muy eficiente. ¡Bien hecho!' if complejidad in ['O(1)', 'O(log n)'] else 'Considera si puedes optimizar el algoritmo.' if complejidad == 'O(n²)' else 'Tu solución tiene una complejidad aceptable.'}"""

        return feedback

    # PISTAS PARA ERRORES DE COMPILACIÓN
    if tiene_error_compilacion:
        pistas = GeneradorPistas.generar_pistas_compilacion(resultados, codigo)

        return "🔧 **Pistas para errores de compilación:**\n\n" + "\n".join(pistas)

    # PISTAS PARA ERRORES DE RUNTIME
    if tiene_error_runtime:
        pistas = GeneradorPistas.generar_pistas_runtime(resultados, codigo)

        return "⚡ **Pistas para errores de ejecución:**\n\n" + "\n".join(pistas)

    # PISTAS PARA PRUEBAS FALLIDAS (lógica)
    if tiene_pruebas_fallidas:
        pistas = GeneradorPistas.generar_pistas_logica(codigo, resultados)

        # Añadir análisis de complejidad incluso para código incorrecto (como referencia)
        complejidad = AnalizadorComplejidad.analizar_complejidad(codigo)

        feedback = f"""🎯 **Pistas para pruebas fallidas:**

{"".join(f"   {pista} " for pista in pistas)}

📊 **Complejidad detectada:** {complejidad}
   (Basado en la estructura actual de tu código)"""

        return feedback

    # Feedback por defecto
    return """💡 **Pistas generales para mejorar tu código:**

• Revisa la lógica paso a paso con ejemplos simples
• Verifica los tipos de datos y conversiones
• Prueba casos extremos (0, vacío, valores máximos)
• Asegúrate de cubrir todos los casos posibles"""


@app.get("/")
async def root():
    return {
        "message": "API de Análisis Inteligente - Activa",
        "status": "ready",
        "version": "4.0.0",
        "features": ["complejidad_algoritmica", "pistas_inteligentes", "analisis_patrones"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "ready",
        "timestamp": time.time(),
        "model": "smart-analyzer-v4"
    }


@app.post("/analyze_solution")
async def analyze_solution(data: SolucionEntrada):
    """
    Analiza código C++ usando análisis inteligente
    """
    try:
        inicio = time.time()

        if not data.codigo_usuario.strip():
            return {
                "status": "error",
                "message": "El código está vacío",
                "feedback_completo": "Por favor, escribe algún código antes de solicitar análisis."
            }

        logger.info(f"🧠 Análisis inteligente - Código: {len(data.codigo_usuario)} chars")

        # Análisis inteligente
        feedback = analizar_codigo_inteligente(data.codigo_usuario, data.resultados_evaluacion)

        tiempo_procesamiento = time.time() - inicio

        logger.info(f"✅ Análisis completado en {tiempo_procesamiento:.2f}s")

        return {
            "status": "success",
            "message": "Análisis inteligente completado",
            "feedback_completo": feedback,
            "tiempo_procesamiento": f"{tiempo_procesamiento:.2f}s",
            "caracteristicas": ["complejidad", "pistas_practicas", "analisis_estructural"]
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