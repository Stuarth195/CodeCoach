// main.cpp - VERSIÓN MEJORADA CON NUEVAS FUNCIONALIDADES
#include <iostream>
#include <string>
#include "RequestHandler.h"
#include "format.h"
#include "json.hpp"

using json = nlohmann::json;

int main()
{
    std::cout << "🚀 Iniciando servidor C++ CodeCoach (HTTP REAL)..." << std::endl;
    std::cout << "📍 Escuchando en: http://localhost:5000" << std::endl;

    RequestHandler handler;

    // Endpoint principal para evaluación
    handler.addRoute("/submit_evaluation", [](const std::string &requestBody)
                     {
        std::cout << "\n🎯 ===== EVALUACIÓN RECIBIDA =====" << std::endl;
        
        // Mostrar JSON completo
        std::cout << "📦 JSON COMPLETO:" << std::endl;
        std::cout << requestBody << std::endl;
        std::cout << "=====================================" << std::endl;
        
        // Crear objeto Format con el JSON recibido
        Format formulario(requestBody);
        
        // Validar el formato
        if (!formulario.esValido()) {
            std::cout << "❌ ERROR: JSON con estructura inválida" << std::endl;
            json errorResponse;
            errorResponse["status"] = "error";
            errorResponse["message"] = "Estructura JSON inválida";
            errorResponse["details"] = "Faltan campos requeridos en el JSON";
            return errorResponse.dump();
        }
        
        // Usar los métodos de la clase para mostrar la información
        formulario.mostrarInformacion();
        
        // Mostrar información adicional con los nuevos métodos
        auto inputs = formulario.getInputs();
        auto outputs = formulario.getOutputsEsperados();
        
        std::cout << "🔢 RESUMEN EJECUCIÓN:" << std::endl;
        std::cout << "   📥 Número de inputs: " << inputs.size() << std::endl;
        std::cout << "   📤 Número de outputs esperados: " << outputs.size() << std::endl;
        std::cout << "   📝 Longitud del código: " << formulario.getCodigo().length() << " caracteres" << std::endl;
        
        std::cout << "✅ FIN DEL ANÁLISIS" << std::endl;
        
        // Construir respuesta JSON usando nlohmann
        json response;
        response["status"] = "success";
        response["message"] = "✅ Código recibido y analizado exitosamente";
        response["server_message"] = "El servidor C++ procesó tu código correctamente";
        
        json details;
        details["usuario_recibido"] = formulario.getNombre();
        details["problema_recibido"] = formulario.getProblemTitle();
        details["dificultad"] = formulario.getDifficulty();
        details["longitud_codigo"] = std::to_string(formulario.getCodigo().length()) + " caracteres";
        details["numero_inputs"] = inputs.size();
        details["numero_outputs"] = outputs.size();
        details["valido"] = formulario.esValido();
        
        response["details"] = details;
        
        return response.dump(); });

    // Endpoint para compilación simple
    handler.addRoute("/submit_code", [](const std::string &requestBody)
                     {
        std::cout << "📥 Código simple recibido:" << std::endl;
        std::cout << requestBody << std::endl;
        
        // También podemos usar Format aquí si el JSON tiene la misma estructura
        try {
            Format codigoSimple(requestBody);
            if (codigoSimple.esValido()) {
                std::cout << "✅ Código válido para compilación" << std::endl;
                std::cout << "📝 Longitud: " << codigoSimple.getCodigo().length() << " caracteres" << std::endl;
            }
        } catch (...) {
            std::cout << "⚠️  JSON no válido para formato esperado" << std::endl;
        }
        
        json response;
        response["status"] = "success";
        response["message"] = "Código recibido para compilación simple";
        return response.dump(); });

    // Iniciar servidor
    handler.startServer(5000);

    return 0;
}