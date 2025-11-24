// main.cpp
#include <iostream>
#include <string>
#include <csignal>
#include <cstdlib>
#include "RequestHandler.h"
#include "format.h"
#include "runner.h"
#include "json.hpp"

using json = nlohmann::json;

// Variable global para manejar la señal de interrupción
volatile sig_atomic_t stop_server = 0;

// Manejador de señal para Ctrl+C
void signalHandler(int signal)
{
    if (signal == SIGINT)
    {
        std::cout << "\n\n🛑 Señal Ctrl+C recibida. Cerrando servidor..." << std::endl;
        stop_server = 1;
    }
}

int main()
{
    // Registrar el manejador de señales para Ctrl+C
    std::signal(SIGINT, signalHandler);

    std::cout << "🚀 Iniciando servidor C++ CodeCoach..." << std::endl;
    std::cout << "📍 Escuchando en: http://localhost:5000" << std::endl;
    std::cout << "💡 Presiona Ctrl+C para detener el servidor" << std::endl;

    RequestHandler handler;

    handler.addRoute("/submit_evaluation", [](const std::string &requestBody)
                     {
    std::cout << "\n🎯 ===== EVALUACIÓN SOLICITADA =====" << std::endl;
    
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
    
    // Usar el namespace runner::
    runner::EvaluationResult detailed_result = runner::evaluate_submission_detailed(requestBody);
    std::string json_response = runner::evaluation_result_to_json(detailed_result);
    
    std::cout << "✅ Runner finalizado. Resultado: " << detailed_result.status << std::endl;
    
    return json_response; });

    // Endpoint auxiliar: Compilación simple (sin tests)
    handler.addRoute("/submit_code", [](const std::string &requestBody)
                     {
        std::cout << "\n📥 Compilación simple recibida." << std::endl;
        // Reutilizamos el runner, este detectará que no hay inputs si no se envían
        // y solo compilará.
        return runner::evaluate_submission(requestBody); });

    // Iniciar servidor
    handler.startServer(5000);

    std::cout << "👋 Servidor cerrado correctamente." << std::endl;
    return 0;
}