// CppServer/main.cpp
#include <iostream>
#include <string>
#include <cstdlib>
#include "RequestHandler.h"

int main()
{
    std::cout << "🚀 Iniciando servidor C++ CodeCoach..." << std::endl;
    std::cout << "📍 Escuchando en: http://localhost:5000" << std::endl;

    // Inicializar cURL globalmente
    curl_global_init(CURL_GLOBAL_ALL);

    // Crear manejador de requests
    RequestHandler handler;

    // Configurar rutas
    handler.addRoute("/submit_evaluation", [](const std::string &requestBody)
                     {
        std::cout << "📥 Recibida solicitud en /submit_evaluation" << std::endl;
        std::cout << "📦 Cuerpo de la solicitud:" << std::endl;
        std::cout << requestBody << std::endl;
        
        // Respuesta de prueba por ahora
        std::string response = R"({
            "status": "success",
            "message": "Servidor C++ recibió la solicitud correctamente",
            "received_data": )" + requestBody + R"(
        })";
        
        return response; });

    handler.addRoute("/submit_code", [](const std::string &requestBody)
                     {
        std::cout << "📥 Recibida solicitud en /submit_code" << std::endl;
        std::cout << "📦 Cuerpo de la solicitud:" << std::endl;
        std::cout << requestBody << std::endl;
        
        std::string response = R"({
            "status": "success", 
            "message": "Código recibido para compilación simple",
            "code_preview": ")" + requestBody.substr(0, 100) + "...\"}";
        
        return response; });

    // Iniciar servidor en puerto 5000
    std::cout << "✅ Servidor listo. Esperando requests..." << std::endl;
    handler.startServer(5000);

    // Limpiar cURL
    curl_global_cleanup();

    return 0;
}