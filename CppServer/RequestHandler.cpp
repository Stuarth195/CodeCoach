// RequestHandler.cpp - SERVIDOR HTTP REAL
#include "RequestHandler.h"
#include <iostream>
#include <thread>
#include <chrono>

RequestHandler::RequestHandler() : serverSocket(-1)
{
    std::cout << "🔧 Inicializando RequestHandler..." << std::endl;
    initializeSocket();
}

RequestHandler::~RequestHandler()
{
    std::cout << "🧹 Limpiando RequestHandler..." << std::endl;
    cleanupSocket();
}

void RequestHandler::initializeSocket()
{
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        std::cerr << "❌ Error inicializando Winsock" << std::endl;
        return;
    }
#endif

    serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket < 0)
    {
        std::cerr << "❌ Error creando socket" << std::endl;
        return;
    }

    // Permitir reutilizar dirección
    int opt = 1;
#ifdef _WIN32
    setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt));
#else
    setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif
}

void RequestHandler::cleanupSocket()
{
#ifdef _WIN32
    if (serverSocket != INVALID_SOCKET)
    {
        closesocket(serverSocket);
    }
    WSACleanup();
#else
    if (serverSocket >= 0)
    {
        close(serverSocket);
    }
#endif
}

std::string RequestHandler::readHttpRequest(int clientSocket)
{
    char buffer[4096];
    std::string request;

#ifdef _WIN32
    int bytesReceived;
#else
    ssize_t bytesReceived;
#endif

    while ((bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0)) > 0)
    {
        buffer[bytesReceived] = '\0';
        request.append(buffer);

        // Si hemos recibido todo el request (termina con \r\n\r\n)
        if (request.find("\r\n\r\n") != std::string::npos)
        {
            // Buscar Content-Length para body
            size_t contentLengthPos = request.find("Content-Length: ");
            if (contentLengthPos != std::string::npos)
            {
                size_t contentLengthEnd = request.find("\r\n", contentLengthPos);
                std::string contentLengthStr = request.substr(
                    contentLengthPos + 16, contentLengthEnd - contentLengthPos - 16);
                int contentLength = std::stoi(contentLengthStr);

                // Leer body completo si existe
                size_t bodyStart = request.find("\r\n\r\n") + 4;
                if (request.length() - bodyStart < contentLength)
                {
                    // Necesitamos leer más datos del body
                    int remaining = contentLength - (request.length() - bodyStart);
                    while (remaining > 0 &&
                           (bytesReceived = recv(clientSocket, buffer,
                                                 std::min(remaining, (int)sizeof(buffer) - 1), 0)) > 0)
                    {
                        buffer[bytesReceived] = '\0';
                        request.append(buffer);
                        remaining -= bytesReceived;
                    }
                }
            }
            break;
        }
    }

    return request;
}

void RequestHandler::sendHttpResponse(int clientSocket, const std::string &response)
{
    std::string httpResponse =
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n"
        "Content-Length: " +
        std::to_string(response.length()) + "\r\n"
                                            "\r\n" +
        response;

#ifdef _WIN32
    send(clientSocket, httpResponse.c_str(), httpResponse.length(), 0);
    closesocket(clientSocket);
#else
    send(clientSocket, httpResponse.c_str(), httpResponse.length(), 0);
    close(clientSocket);
#endif
}

std::string RequestHandler::parseJsonFromRequest(const std::string &httpRequest)
{
    size_t jsonStart = httpRequest.find("\r\n\r\n");
    if (jsonStart != std::string::npos)
    {
        return httpRequest.substr(jsonStart + 4);
    }
    return "{}";
}

void RequestHandler::addRoute(const std::string &path, std::function<std::string(const std::string &)> handler)
{
    routes[path] = handler;
    std::cout << "📍 Ruta registrada: " << path << std::endl;
}

void RequestHandler::startServer(int port)
{
    if (serverSocket < 0)
    {
        std::cerr << "❌ Socket no válido" << std::endl;
        return;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    serverAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(serverSocket, (sockaddr *)&serverAddr, sizeof(serverAddr)) < 0)
    {
        std::cerr << "❌ Error en bind()" << std::endl;
        return;
    }

    if (listen(serverSocket, 10) < 0)
    {
        std::cerr << "❌ Error en listen()" << std::endl;
        return;
    }

    std::cout << "🚀 Servidor HTTP REAL iniciado en puerto: " << port << std::endl;
    std::cout << "📍 Esperando conexiones en: http://localhost:" << port << std::endl;

    while (true)
    {
        sockaddr_in clientAddr;
#ifdef _WIN32
        int clientAddrLen = sizeof(clientAddr);
#else
        socklen_t clientAddrLen = sizeof(clientAddr);
#endif

#ifdef _WIN32
        SOCKET clientSocket = accept(serverSocket, (sockaddr *)&clientAddr, &clientAddrLen);
#else
        int clientSocket = accept(serverSocket, (sockaddr *)&clientAddr, &clientAddrLen);
#endif

        if (clientSocket < 0)
        {
            std::cerr << "❌ Error aceptando conexión" << std::endl;
            continue;
        }

        // Leer el request HTTP
        std::string httpRequest = readHttpRequest(clientSocket);

        // Extraer método y path
        std::istringstream requestStream(httpRequest);
        std::string method, path, protocol;
        requestStream >> method >> path >> protocol;

        std::cout << "\n🎯 ===== NUEVA CONEXIÓN =====" << std::endl;
        std::cout << "📨 Método: " << method << std::endl;
        std::cout << "📍 Path: " << path << std::endl;

        // Manejar CORS preflight
        if (method == "OPTIONS")
        {
            sendHttpResponse(clientSocket, "{}");
            continue;
        }

        // Buscar handler para la ruta
        std::string response;
        if (routes.find(path) != routes.end())
        {
            // Extraer JSON del body
            std::string jsonBody = parseJsonFromRequest(httpRequest);

            std::cout << "📦 JSON RECIBIDO:" << std::endl;
            std::cout << "=====================================" << std::endl;
            std::cout << jsonBody << std::endl;
            std::cout << "=====================================" << std::endl;

            // Ejecutar handler
            response = routes[path](jsonBody);
        }
        else
        {
            response = R"({"status": "error", "message": "Ruta no encontrada"})";
        }

        // Enviar respuesta
        sendHttpResponse(clientSocket, response);
    }
}