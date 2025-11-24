# analizador_api.py - VERSIÓN CON IA GENERATIVA MEJORADA
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from fastapi import FastAPI
from pydantic import BaseModel
import logging
import time
import re
from typing import List, Dict
import requests
import json

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
    title="Analizador de Soluciones CodeCoach - IA Generativa",
    description="API para análisis de complejidad y feedback generativo",
    version="5.0.0"
)


class AnalizadorComplejidad:
    """Analiza la complejidad algorítmica del código C++ de manera generativa"""

    @staticmethod
    def analizar_complejidad_generativa(codigo: str) -> str:
        """Analiza complejidad de manera más inteligente y generativa"""

        codigo_limpio = re.sub(r'//.*$', '', codigo, flags=re.MULTILINE)
        codigo_limpio = re.sub(r'/\*.*?\*/', '', codigo_limpio, flags=re.DOTALL)

        lineas = codigo_limpio.split('\n')
        complejidad_base = "O(1)"

        # Detectar patrones más avanzados
        bucles_simples = 0
        bucles_anidados = 0
        nivel_anidamiento = 0
        llamadas_recursivas = 0

        for linea in lineas:
            linea_limpia = linea.strip()

            # Detectar bucles
            if re.search(r'\b(for|while)\s*\(', linea_limpia):
                nivel_anidamiento += 1
                if nivel_anidamiento == 1:
                    bucles_simples += 1
                elif nivel_anidamiento == 2:
                    bucles_anidados += 1

            # Detectar fin de bloque
            if re.search(r'^\s*\}', linea_limpia) or re.search(r'\}\s*;?\s*$', linea_limpia):
                nivel_anidamiento = max(0, nivel_anidamiento - 1)

            # Detectar recursión
            nombre_funcion = AnalizadorComplejidad._extraer_nombre_funcion(codigo)
            if nombre_funcion and re.search(r'\b' + re.escape(nombre_funcion) + r'\s*\(', linea_limpia):
                llamadas_recursivas += 1

        # Lógica generativa mejorada
        if bucles_anidados >= 2:
            complejidad_base = "O(n³)"
        elif bucles_anidados >= 1:
            complejidad_base = "O(n²)"
        elif bucles_simples >= 1:
            if llamadas_recursivas >= 2:
                complejidad_base = "O(2^n)"  # Recursión múltiple
            elif llamadas_recursivas == 1:
                complejidad_base = "O(n)"  # Recursión simple
            else:
                complejidad_base = "O(n)"

        # Detectar algoritmos específicos
        if AnalizadorComplejidad._es_busqueda_binaria(codigo):
            complejidad_base = "O(log n)"
        elif AnalizadorComplejidad._es_ordenamiento(codigo):
            complejidad_base = "O(n log n)"

        return complejidad_base

    @staticmethod
    def _extraer_nombre_funcion(codigo: str) -> str:
        match = re.search(r'(?:bool|int|double|string|void|vector<\w+>|list<\w+>)\s+(\w+)\s*\(', codigo)
        return match.group(1) if match else "main"

    @staticmethod
    def _es_busqueda_binaria(codigo: str) -> bool:
        patrones = [
            r'while\s*\(\s*left\s*<=\s*right\s*\)',
            r'while\s*\(\s*low\s*<=\s*high\s*\)',
            r'mid\s*=\s*(?:left\s*\+\s*right|low\s*\+\s*high)\s*/\s*2',
            r'middle\s*='
        ]
        return any(re.search(patron, codigo, re.IGNORECASE) for patron in patrones)

    @staticmethod
    def _es_ordenamiento(codigo: str) -> bool:
        patrones = [
            r'for\s*\(\s*int\s+i\s*=\s*0\s*;\s*i\s*<\s*n\s*;\s*i\+\+\s*\)\s*\{[^}]*for\s*\(\s*int\s+j\s*=\s*0\s*;\s*j\s*<\s*n\s*-\s*i\s*-\s*1\s*;\s*j\+\+\s*\)',
            r'merge\s*\(|quick\s*sort|heap\s*sort',
            r'sort\s*\('
        ]
        return any(re.search(patron, codigo, re.IGNORECASE) for patron in patrones)


class GeneradorFeedbackIA:
    """Genera feedback generativo usando análisis inteligente"""

    @staticmethod
    def generar_feedback_completo(codigo: str, resultados: str, enunciado: str = "") -> str:
        """Genera feedback generativo completo basado en el análisis del código"""

        # Determinar el contexto del problema
        tiene_error_compilacion = any(term in resultados.lower() for term in
                                      ["compile_error", "error de compilación", "compilation error"])
        tiene_error_runtime = any(term in resultados.lower() for term in
                                  ["runtime_error", "timeout", "segmentation"])
        tiene_pruebas_fallidas = any(term in resultados.lower() for term in
                                     ["failed", "fallidas", "incorrecto"])
        es_exitoso = "success" in resultados.lower() and not tiene_pruebas_fallidas

        # Análisis de complejidad
        complejidad = AnalizadorComplejidad.analizar_complejidad_generativa(codigo)

        # Generar feedback según el escenario
        if es_exitoso:
            return GeneradorFeedbackIA._feedback_exitoso(complejidad, codigo)
        elif tiene_error_compilacion:
            return GeneradorFeedbackIA._feedback_errores_compilacion(codigo, resultados)
        elif tiene_error_runtime:
            return GeneradorFeedbackIA._feedback_errores_runtime(codigo, resultados)
        elif tiene_pruebas_fallidas:
            return GeneradorFeedbackIA._feedback_pruebas_fallidas(codigo, resultados, complejidad)
        else:
            return GeneradorFeedbackIA._feedback_general(codigo, complejidad)

    @staticmethod
    def _feedback_exitoso(complejidad: str, codigo: str) -> str:
        """Feedback para código exitoso"""

        eficiencia = GeneradorFeedbackIA._evaluar_eficiencia(complejidad)
        sugerencias = GeneradorFeedbackIA._generar_sugerencias_mejora(codigo, complejidad)

        feedback = f"""🎉 **¡Excelente trabajo! Tu solución es correcta.**

📊 **Análisis de Complejidad:**
   - **Complejidad temporal:** {complejidad}
   - **Eficiencia:** {eficiencia['nivel']}
   - **Evaluación:** {eficiencia['evaluacion']}

💡 **Sugerencias de mejora:**
{sugerencias}

🔍 **Análisis detallado:**
{GeneradorFeedbackIA._analizar_estructuras_code(codigo)}"""

        return feedback

    @staticmethod
    def _feedback_errores_compilacion(codigo: str, resultados: str) -> str:
        """Feedback generativo para errores de compilación"""

        errores_comunes = GeneradorFeedbackIA._identificar_errores_compilacion(codigo, resultados)
        pistas = GeneradorFeedbackIA._generar_pistas_compilacion(errores_comunes)

        feedback = f"""🔧 **Se detectaron errores de compilación**

📝 **Posibles problemas identificados:**
{errores_comunes}

💡 **Pistas para resolverlos:**
{pistas}

🛠️ **Verifica especialmente:**
{GeneradorFeedbackIA._verificar_sintaxis_basica(codigo)}"""

        return feedback

    @staticmethod
    def _feedback_errores_runtime(codigo: str, resultados: str) -> str:
        """Feedback generativo para errores de runtime"""

        posibles_causas = GeneradorFeedbackIA._analizar_causas_runtime(codigo, resultados)
        estrategias = GeneradorFeedbackIA._generar_estrategias_debugging(codigo)

        feedback = f"""⚡ **Error durante la ejecución**

🔍 **Posibles causas identificadas:**
{posibles_causas}

🎯 **Estrategias de debugging:**
{estrategias}

⚠️ **Puntos críticos a revisar:**
{GeneradorFeedbackIA._identificar_puntos_criticos(codigo)}"""

        return feedback

    @staticmethod
    def _feedback_pruebas_fallidas(codigo: str, resultados: str, complejidad: str) -> str:
        """Feedback generativo para pruebas fallidas"""

        patrones_error = GeneradorFeedbackIA._identificar_patrones_error(codigo, resultados)
        sugerencias_logica = GeneradorFeedbackIA._sugerir_mejoras_logica(codigo)

        feedback = f"""🎯 **Algunas pruebas no pasaron**

📊 **Complejidad actual:** {complejidad}

🔎 **Patrones de error detectados:**
{patrones_error}

💡 **Sugerencias para mejorar la lógica:**
{sugerencias_logica}

🧪 **Considera estos casos:**
{GeneradorFeedbackIA._sugerir_casos_prueba(codigo)}"""

        return feedback

    @staticmethod
    def _feedback_general(codigo: str, complejidad: str) -> str:
        """Feedback general generativo"""

        feedback = f"""🤖 **Análisis Generativo de tu Código**

📊 **Complejidad algorítmica detectada:** {complejidad}

🔍 **Estructuras identificadas:**
{GeneradorFeedbackIA._analizar_estructuras_code(codigo)}

💡 **Recomendaciones generales:**
{GeneradorFeedbackIA._generar_recomendaciones_generales(codigo)}

🎯 **Para mejorar tu solución:**
{GeneradorFeedbackIA._sugerir_enfoques_alternativos(codigo)}"""

        return feedback

    # Métodos auxiliares para generación de contenido
    @staticmethod
    def _evaluar_eficiencia(complejidad: str) -> Dict:
        eficiencia_map = {
            "O(1)": {"nivel": "Óptima", "evaluacion": "Excelente - complejidad constante"},
            "O(log n)": {"nivel": "Muy Buena", "evaluacion": "Muy eficiente - escala logarítmicamente"},
            "O(n)": {"nivel": "Buena", "evaluacion": "Eficiente - escala linealmente"},
            "O(n log n)": {"nivel": "Aceptable", "evaluacion": "Buena para ordenamientos"},
            "O(n²)": {"nivel": "Mejorable", "evaluacion": "Considera optimizar bucles anidados"},
            "O(n³)": {"nivel": "Ineficiente", "evaluacion": "Necesita optimización urgente"},
            "O(2^n)": {"nivel": "Muy Ineficiente", "evaluacion": "Solo viable para problemas pequeños"}
        }
        return eficiencia_map.get(complejidad, {"nivel": "Desconocida", "evaluacion": "Complejidad no determinada"})

    @staticmethod
    def _generar_sugerencias_mejora(codigo: str, complejidad: str) -> str:
        sugerencias = []

        if complejidad in ["O(n²)", "O(n³)"]:
            sugerencias.append("• Podrías explorar técnicas de divide y vencerás")
            sugerencias.append("• Considera usar tablas hash para acceso rápido")
            sugerencias.append("• Revisa si hay cálculos redundantes que puedas memoizar")

        if "vector" in codigo and "reserve" not in codigo:
            sugerencias.append("• Para vectores grandes, considera usar reserve() para mejor performance")

        if "recursion" in codigo.lower() or "recursiv" in codigo.lower():
            sugerencias.append("• La recursión puede optimizarse con iteración o memoización")

        if not sugerencias:
            sugerencias.append("• Tu código ya es bastante eficiente")
            sugerencias.append("• Podrías mejorar la legibilidad con nombres más descriptivos")
            sugerencias.append("• Considera añadir comentarios para partes complejas")

        return "\n".join(sugerencias[:3])

    @staticmethod
    def _identificar_errores_compilacion(codigo: str, resultados: str) -> str:
        errores = []

        if "expected" in resultados and ";" in resultados:
            errores.append("• Puntos y coma faltantes en algunas líneas")

        if "undefined" in resultados or "not declared" in resultados:
            errores.append("• Variables o funciones no declaradas")
            errores.append("• Posibles includes faltantes")

        if "expected" in resultados and ")" in resultados:
            errores.append("• Paréntesis no balanceados en condiciones")

        # Verificar bibliotecas
        bibliotecas_faltantes = GeneradorFeedbackIA._detectar_bibliotecas_faltantes(codigo)
        if bibliotecas_faltantes:
            errores.extend(bibliotecas_faltantes)

        if not errores:
            errores.append("• Revisa la sintaxis línea por línea")
            errores.append("• Verifica que todos los { } estén balanceados")

        return "\n".join(errores[:4])

    @staticmethod
    def _detectar_bibliotecas_faltantes(codigo: str) -> List[str]:
        faltantes = []
        bibliotecas = {
            "vector": "#include <vector>",
            "string": "#include <string>",
            "list": "#include <list>",
            "algorithm": "#include <algorithm>",
            "map": "#include <map>",
            "set": "#include <set>"
        }

        for lib, include in bibliotecas.items():
            if lib in codigo and include not in codigo:
                faltantes.append(f"• Para usar {lib}, necesitas: {include}")

        return faltantes

    @staticmethod
    def _generar_pistas_compilacion(errores: str) -> str:
        pistas = [
            "• Revisa cada línea cuidadosamente desde el principio",
            "• Usa un IDE con resaltado de sintaxis para detectar errores",
            "• Compila frecuentemente para detectar errores temprano",
            "• Verifica que todos los namespaces estén correctos"
        ]
        return "\n".join(pistas[:3])

    @staticmethod
    def _analizar_causas_runtime(codigo: str, resultados: str) -> str:
        causas = []

        if "timeout" in resultados.lower():
            causas.append("• Posible bucle infinito")
            causas.append("• Algoritmo muy lento para los casos grandes")
            causas.append("• Condición de salida incorrecta en bucles")

        if "segmentation" in resultados.lower():
            causas.append("• Acceso a memoria fuera de límites")
            causas.append("• Punteros no inicializados")
            causas.append("• Desbordamiento de buffers")

        if "division" in resultados.lower() and "zero" in resultados.lower():
            causas.append("• División por cero")

        if not causas:
            causas.append("• Comportamiento indefinido en alguna operación")
            causas.append("• Manejo incorrecto de memoria")
            causas.append("• Condiciones de carrera en operaciones")

        return "\n".join(causas[:3])

    @staticmethod
    def _generar_estrategias_debugging(codigo: str) -> str:
        estrategias = [
            "• Usa prints estratégicos para seguir el flujo",
            "• Prueba con inputs pequeños y simples",
            "• Revisa condiciones límite y casos extremos",
            "• Verifica que todas las variables estén inicializadas"
        ]

        if "recursion" in codigo.lower():
            estrategias.append("• Revisa el caso base de la recursión")
            estrategias.append("• Verifica que no haya recursión infinita")

        if "pointer" in codigo.lower() or "new" in codigo:
            estrategias.append("• Verifica que toda memoria allocada se libere")

        return "\n".join(estrategias[:4])

    @staticmethod
    def _identificar_puntos_criticos(codigo: str) -> str:
        puntos = []

        lineas = codigo.split('\n')
        for i, linea in enumerate(lineas, 1):
            if "while" in linea and "true" in linea.lower():
                puntos.append(f"• Línea {i}: Bucle while(true) - verifica condición de salida")
            if "recursion" in linea.lower():
                puntos.append(f"• Línea {i}: Llamada recursiva - verifica caso base")
            if "pointer" in linea.lower() or "new " in linea:
                puntos.append(f"• Línea {i}: Manejo de memoria - verifica alloc/liberación")

        if not puntos:
            puntos.append("• Bucles while/for - condiciones de terminación")
            puntos.append("• Accesos a arrays/vectores - índices válidos")
            puntos.append("• Operaciones matemáticas - división por cero")

        return "\n".join(puntos[:3])

    @staticmethod
    def _identificar_patrones_error(codigo: str, resultados: str) -> str:
        patrones = []

        if "if" in codigo and "else" not in codigo:
            patrones.append("• Posible caso no cubierto (falta else)")

        if codigo.count("return") < 2 and "void" not in codigo:
            patrones.append("• Posible ruta sin retorno de valor")

        if "vector" in codigo or "array" in codigo:
            patrones.append("• Posible acceso fuera de límites")
            patrones.append("• Índices incorrectos en bucles")

        if "=" in codigo and "==" not in codigo:
            patrones.append("• Posible asignación en lugar de comparación")

        if not patrones:
            patrones.append("• Lógica condicional incorrecta")
            patrones.append("• Manejo incorrecto de casos edge")
            patrones.append("• Error en transformación de datos")

        return "\n".join(patrones[:3])

    @staticmethod
    def _sugerir_mejoras_logica(codigo: str) -> str:
        sugerencias = []

        if "for" in codigo and "++" in codigo:
            sugerencias.append("• Verifica los límites de los bucles")
            sugerencias.append("• Considera si necesitas iterar en otro orden")

        if "if" in codigo and codigo.count("if") > 3:
            sugerencias.append("• Podrías simplificar condiciones anidadas")
            sugerencias.append("• Considera usar switch o lookup tables")

        if "vector" in codigo and "sort" not in codigo:
            sugerencias.append("• Para búsquedas frecuentes, considera ordenar primero")

        if not sugerencias:
            sugerencias.append("• Prueba tu lógica con ejemplos paso a paso")
            sugerencias.append("• Considera casos extremos (0, vacío, máximo)")
            sugerencias.append("• Divide el problema en subproblemas más pequeños")

        return "\n".join(sugerencias[:3])

    @staticmethod
    def _sugerir_casos_prueba(codigo: str) -> str:
        casos = [
            "• Caso vacío (0, string vacío, vector vacío)",
            "• Caso con un solo elemento",
            "• Caso con valores máximos/mínimos",
            "• Caso con datos desordenados (si aplica)"
        ]
        return "\n".join(casos)

    @staticmethod
    def _analizar_estructuras_code(codigo: str) -> str:
        estructuras = []

        if "vector" in codigo:
            estructuras.append("• Vectores: estructura de array dinámico")
        if "list" in codigo:
            estructuras.append("• Listas: estructura enlazada para inserciones frecuentes")
        if "recursion" in codigo.lower():
            estructuras.append("• Recursión: útil para problemas divisibles")
        if "sort" in codigo:
            estructuras.append("• Algoritmos de ordenamiento")

        if not estructuras:
            estructuras.append("• Estructuras básicas y bucles")
            estructuras.append("• Lógica condicional estándar")

        return "\n".join(estructuras[:3])

    @staticmethod
    def _generar_recomendaciones_generales(codigo: str) -> str:
        recomendaciones = [
            "• Escribe código auto-documentado con nombres claros",
            "• Mantén las funciones pequeñas y con un solo propósito",
            "• Comenta las partes no obvias de tu lógica",
            "• Prueba con diferentes casos antes de enviar"
        ]
        return "\n".join(recomendaciones[:3])

    @staticmethod
    def _sugerir_enfoques_alternativos(codigo: str) -> str:
        enfoques = []

        if "O(n²)" in AnalizadorComplejidad.analizar_complejidad_generativa(codigo):
            enfoques.append("• Considera usar un set o map para O(1) búsquedas")
            enfoques.append("• Explora el enfoque de dos punteros")
            enfoques.append("• Podrías ordenar primero para luego usar búsqueda binaria")

        if "recursion" in codigo.lower():
            enfoques.append("• Podrías implementar una versión iterativa")
            enfoques.append("• Considera memoización para evitar cálculos repetidos")

        if not enfoques:
            enfoques.append("• Revisa patrones comunes de resolución")
            enfoques.append("• Considera dividir el problema en partes más manejables")
            enfoques.append("• Busca simetrías o propiedades matemáticas del problema")

        return "\n".join(enfoques[:3])

    @staticmethod
    def _verificar_sintaxis_basica(codigo: str) -> str:
        verificaciones = [
            "• Puntos y coma al final de cada statement",
            "• Paréntesis balanceados en condiciones",
            "• Llaves {} balanceadas",
            "• Includes necesarios para las estructuras usadas"
        ]
        return "\n".join(verificaciones)


@app.get("/")
async def root():
    return {
        "message": "API de Análisis Generativo - Activa",
        "status": "ready",
        "version": "5.0.0",
        "features": ["complejidad_generativa", "feedback_inteligente", "analisis_avanzado"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "ready",
        "timestamp": time.time(),
        "model": "generative-analyzer-v5"
    }


@app.post("/analyze_solution")
async def analyze_solution(data: SolucionEntrada):
    """
    Analiza código C++ usando IA generativa para feedback
    """
    try:
        inicio = time.time()

        if not data.codigo_usuario.strip():
            return {
                "status": "error",
                "message": "El código está vacío",
                "feedback_completo": "Por favor, escribe algún código antes de solicitar análisis."
            }

        logger.info(f"🧠 Análisis generativo - Código: {len(data.codigo_usuario)} chars")

        # Análisis generativo
        feedback = GeneradorFeedbackIA.generar_feedback_completo(
            data.codigo_usuario,
            data.resultados_evaluacion,
            data.problema_enunciado
        )

        tiempo_procesamiento = time.time() - inicio

        logger.info(f"✅ Análisis generativo completado en {tiempo_procesamiento:.2f}s")

        return {
            "status": "success",
            "message": "Análisis generativo completado",
            "feedback_completo": feedback,
            "tiempo_procesamiento": f"{tiempo_procesamiento:.2f}s",
            "caracteristicas": ["complejidad_generativa", "feedback_contextual", "pistas_practicas"]
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