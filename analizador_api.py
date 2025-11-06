from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

"""
Estructura de Datos de Entrada
"""
# Define cómo se verán los datos que enviará el motor de C++
class SolucionEntrada(BaseModel):

    #Define el esquema de datos que la API espera recibir.

    codigo_usuario: str
    resultados_evaluacion: str # Texto que describe el resultado de la compilación/tests
    problema_enunciado: str   # Descripción del problema para darle contexto al LLM
    lenguaje: str = "C++"     # Opcional: Para indicar el lenguaje

# Inicializa la aplicación FastAPI
app = FastAPI(title="Analizador de Soluciones CodeCoach")



"""
Cargar el pipeline de generación de texto para GPT-J.
NOTA: Cargar modelos grandes como GPT-J (6B) requiere mucha RAM (aprox. 16GB VRAM/RAM). 
Si el modelo es demasiado grande, se recomienda usar una API externa (como la de NLP Cloud)
o un modelo más pequeño. Para este ejemplo, usamos un modelo de generación genérico.
Si el nombre del modelo EleutherAI/gpt-j-6B no funciona por falta de recursos, 
puedes probar un modelo más pequeño como 'gpt2' para la prueba inicial. 
"""

try:
    # Intenta cargar GPT-J (puede ser un proceso lento y requerir muchos recursos)
    #generador_llm = pipeline("text-generation", model="EleutherAI/gpt-j-6B")
    generador_llm = pipeline("text-generation", model="gpt2")
except Exception:
    # Si GPT-J falla por recursos, usa GPT-2 como fallback para la estructura
    print("ADVERTENCIA: No se pudo cargar GPT-J (6B). Usando 'gpt2' como ejemplo de prueba.")
    generador_llm = pipeline("text-generation", model="gpt2")


def generar_prompt_para_coach(data: SolucionEntrada) -> str:
    """
    # Construye el prompt detallado que guiará a GPT-J.
    """
    # El prompt debe ser muy específico en el rol y el formato de salida
    prompt = f"""
    Eres un Code Coach experto para una plataforma de aprendizaje. Tu tarea es analizar el código del estudiante y proporcionar feedback constructivo y educativo.

    **Instrucciones CLAVE (No las olvides):**
    1. **NO** debes dar la solución completa ni el código corregido.
    2. Estima la **Complejidad Algorítmica** (Notación Big O) e identifica el **Tipo de Algoritmo** usado.
    3. Proporciona **Feedback** estructurado en tres secciones: Pista/Explicación del Error (si falla), Sugerencia de Eficiencia (si es lento) y Recomendación de Optimización.

    **Problema:**
    {data.problema_enunciado}

    **Código del Estudiante (Lenguaje: {data.lenguaje}):**
    ```
    {data.codigo_usuario}
    ```

    **Resultados de la Evaluación (Compilación y Pruebas):**
    {data.resultados_evaluacion}

    **Genera tu análisis y feedback con el siguiente formato estricto:**
    Complejidad Estimada: O(...) (Tipo: Algoritmo de ...)
    Feedback del Coach:
    * Pista/Explicación de Error: ...
    * Sugerencia de Eficiencia: ...
    * Recomendación de Optimización: ...
    """
    return prompt


def llamar_llm(prompt: str) -> str:
    """
    Realiza la llamada al LLM (GPT-J o GPT-2) y obtiene la respuesta.
    """
    # Configuración de generación para evitar repeticiones y controlar la longitud
    output = generador_llm(
        prompt,
        max_length=600,  # Limita la longitud máxima de la respuesta
        do_sample=True,
        temperature=0.7,  # Controla la creatividad (un poco de creatividad es útil para el feedback)
        top_k=50,
        top_p=0.95,
        num_return_sequences=1
    )

    # Extrae solo el texto generado y elimina el prompt original de la respuesta
    texto_generado = output[0]['generated_text']
    # Eliminar la parte del prompt para devolver solo la respuesta del LLM
    respuesta_limpia = texto_generado.replace(prompt, '').strip()
    return respuesta_limpia


"""
Definición del Endpoint API
"""
@app.post("/analyze_solution")
def analyze_solution(data: SolucionEntrada):
    """
    Recibe el código y los resultados de evaluación, genera el prompt,
    llama al LLM y devuelve el feedback.
    """
    try:
        # 1. Generar el Prompt completo
        prompt_final = generar_prompt_para_coach(data)

        # 2. Llamar al LLM para obtener el feedback
        feedback_llm = llamar_llm(prompt_final)

        # Opcional: Añadir lógica para parsear la respuesta estructurada del LLM aquí,
        # pero por ahora devolvemos el texto completo.

        # 3. Devolver la respuesta al motor de C++
        return {
            "status": "success",
            "message": "Análisis completado",
            "feedback_completo": feedback_llm
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Ocurrió un error en el Analizador de Soluciones: {e}",
            "feedback_completo": ""
        }




