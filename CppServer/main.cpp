// main.cpp - CON MANEJO DETALLADO DE JSON
#include <iostream>
#include <string>
#include "RequestHandler.h"
#include "format.h"

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
        
        // Crear objeto Format con el JSON recibido. Este es el objeto a redireccionar para compilacion o en todo caso sus atributos 
        // los atriibutos estan en el .h por si se quieren revisar los nombres  
        Format formulario(requestBody);
        
        // Usar los métodos de la clase para mostrar la información
        formulario.mostrarInformacion(); //este printea todo
        
        std::cout << "✅ FIN DEL ANÁLISIS" << std::endl;
        
        // Respuesta de éxito
        return R"({
            "status": "success",
            "message": "✅ Código recibido y analizado exitosamente",
            "server_message": "El servidor C++ procesó tu código correctamente",
            "details": {
                "usuario_recibido": ")" + formulario.getNombre() + R"(",
                "problema_recibido": ")" + formulario.getProblemTitle() + R"(",
                "dificultad": ")" + formulario.getDifficulty() + R"(",
                "longitud_codigo": ")" + std::to_string(formulario.getCodigo().length()) + R"( caracteres"
            }
        })"; });

    // retorna todo el fomatop taol y como lo evio

    // Resto del código igual...
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