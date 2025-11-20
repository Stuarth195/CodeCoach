// main.cpp
#include <iostream>
#include <string>
#include "RequestHandler.h"
#include "format.h"
#include "runner.h" // Incluimos el nuevo runner
#include "json.hpp"

using json = nlohmann::json;

int main()
{
    std::cout << "🚀 Iniciando servidor C++ CodeCoach..." << std::endl;
    std::cout << "📍 Escuchando en: http://localhost:5000" << std::endl;

    RequestHandler handler;

    // Endpoint principal: Evaluar código
    handler.addRoute("/submit_evaluation", [](const std::string &requestBody)
    {
        std::cout << "\n🎯 ===== EVALUACIÓN SOLICITADA =====" << std::endl;
        
        // 1. Analizar formato para loguear y validar
        Format formulario(requestBody);
        
        if (!formulario.esValido()) {
            std::cout << "❌ ERROR: JSON inválido o faltan campos." << std::endl;
            json errorResponse;
            errorResponse["status"] = "error";
            errorResponse["message"] = "Estructura JSON inválida (requiere nombre y codigo)";
            return errorResponse.dump();
        }
        
        formulario.mostrarInformacion();
        
        std::cout << "⚙️  Invocando Runner (compilación y ejecución)..." << std::endl;
        
        // 2. Llamar a la lógica del runner
        // Pasamos el JSON crudo, el runner se encarga de extraer inputs/outputs
        std::string runnerJsonResult = runner::evaluate_submission(requestBody);
        
        std::cout << "✅ Runner finalizado." << std::endl;
        
        // 3. Retornar directamente la respuesta del runner
        // (O podrías envolverla si necesitas añadir metadatos del servidor)
        return runnerJsonResult;
    });

    // Endpoint auxiliar: Compilación simple (sin tests)
    handler.addRoute("/submit_code", [](const std::string &requestBody)
    {
        std::cout << "\n📥 Compilación simple recibida." << std::endl;
        // Reutilizamos el runner, este detectará que no hay inputs si no se envían
        // y solo compilará.
        return runner::evaluate_submission(requestBody);
    });

    handler.startServer(5000);

    return 0;
}