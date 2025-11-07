// main.cpp - CON MANEJO DETALLADO DE JSON
#include <iostream>
#include <string>
#include "RequestHandler.h"

// Función simple para extraer campos del JSON (sin librerías externas)
std::string extractField(const std::string &json, const std::string &field)
{
    std::string pattern = "\"" + field + "\":\"";
    size_t start = json.find(pattern);
    if (start == std::string::npos)
    {
        pattern = "\"" + field + "\": \"";
        start = json.find(pattern);
        if (start == std::string::npos)
            return "NO_ENCONTRADO";
    }
    start += pattern.length();
    size_t end = json.find("\"", start);
    if (end == std::string::npos)
        return "ERROR";
    return json.substr(start, end - start);
}

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
        
        // Extraer y mostrar campos importantes
        std::string nombre = extractField(requestBody, "nombre");
        std::string codigo = extractField(requestBody, "codigo");
        std::string problem_title = extractField(requestBody, "problem_title");
        std::string difficulty = extractField(requestBody, "difficulty");
        
        std::cout << "🔍 CAMPOS EXTRAÍDOS:" << std::endl;
        std::cout << "   👤 Usuario: " << nombre << std::endl;
        std::cout << "   📝 Problema: " << problem_title << std::endl;
        std::cout << "   🎚 Dificultad: " << difficulty << std::endl;
        std::cout << "   📄 Código (primeros 100 chars): " 
                  << codigo.substr(0, 100) << "..." << std::endl;
        
        // Extraer inputs/outputs
        for (int i = 1; i <= 3; i++) {
            std::string input = extractField(requestBody, "input" + std::to_string(i));
            std::string output = extractField(requestBody, "output_esperado" + std::to_string(i));
            if (input != "NO_ENCONTRADO" && !input.empty()) {
                std::cout << "   📥 Input " << i << ": " << input << std::endl;
                std::cout << "   📤 Output " << i << ": " << output << std::endl;
            }
        }
        
        std::cout << "✅ FIN DEL ANÁLISIS" << std::endl;
        
        // Respuesta de éxito
        return R"({
            "status": "success",
            "message": "✅ Código recibido y analizado exitosamente",
            "server_message": "El servidor C++ procesó tu código correctamente",
            "details": {
                "usuario_recibido": ")" + nombre + R"(",
                "problema_recibido": ")" + problem_title + R"(",
                "dificultad": ")" + difficulty + R"(",
                "longitud_codigo": ")" + std::to_string(codigo.length()) + R"( caracteres"
            }
        })"; });

    // Endpoint simple para pruebas
    handler.addRoute("/submit_code", [](const std::string &requestBody)
                     {
        std::cout << "📥 Código simple recibido:" << std::endl;
        std::cout << requestBody << std::endl;
        
        return R"({
            "status": "success", 
            "message": "Código recibido para compilación simple"
        })"; });

    // Iniciar servidor
    handler.startServer(5000);

    return 0;
}