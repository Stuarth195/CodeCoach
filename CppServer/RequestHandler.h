// RequestHandler.h
#ifndef REQUESTHANDLER_H
#define REQUESTHANDLER_H

#include <iostream>
#include <string>
#include <functional>
#include <map>
#include <sstream>
#include <curl/curl.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#endif

class RequestHandler
{
private:
    std::map<std::string, std::function<std::string(const std::string &)>> routes;

#ifdef _WIN32
    SOCKET serverSocket;
#else
    int serverSocket;
#endif

    void initializeSocket();
    void cleanupSocket();
    std::string readHttpRequest(int clientSocket);
    void sendHttpResponse(int clientSocket, const std::string &response);
    std::string parseJsonFromRequest(const std::string &httpRequest);

public:
    struct EvalRequest
    {
        std::string submission_id;
        std::string user_code;     // Codigo del usuario (solo la funcion)
        std::string function_name; // Nombre de la funcion a llamar (ej: "esPalindromo")
        std::string function_type; // ✅ NUEVO: Tipo de la función
        std::string filename;      // Por defecto main.cpp

        int compile_timeout_s = 10;
        int run_timeout_s = 2;

        // Vector de pares (input_arg_code, expected_stdout)
        // Nota: input_arg_code se inyectará tal cual en el código C++.
        // Si es string debe venir con comillas desde el JSON o manejarse aqui.
        std::vector<std::pair<std::string, std::string>> tests;
    };

    RequestHandler();
    ~RequestHandler();

    void addRoute(const std::string &path, std::function<std::string(const std::string &)> handler);
    void startServer(int port);
};

#endif