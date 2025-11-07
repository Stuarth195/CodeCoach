// RequestHandler.cpp - VERIFICA QUE TENGA ESTO
#include "RequestHandler.h"
#include <iostream>

// CONSTRUCTOR
RequestHandler::RequestHandler()
{
    std::cout << "🔧 Inicializando RequestHandler..." << std::endl;
}

// DESTRUCTOR
RequestHandler::~RequestHandler()
{
    std::cout << "🧹 Limpiando RequestHandler..." << std::endl;
}

// MÉTODO addRoute
void RequestHandler::addRoute(const std::string &path, RouteHandler handler)
{
    routes[path] = handler;
    std::cout << "📍 Ruta registrada: " << path << std::endl;
}

// MÉTODO startServer (aunque sea vacío por ahora)
void RequestHandler::startServer(int port)
{
    std::cout << "🚀 Servidor iniciado en puerto: " << port << std::endl;
    // Por ahora solo imprime
    while (true)
    {
        // Mantener el programa corriendo
    }
}