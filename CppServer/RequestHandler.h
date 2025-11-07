// CppServer/RequestHandler.h
#ifndef REQUESTHANDLER_H
#define REQUESTHANDLER_H

#include <string>
#include <functional>
#include <map>
#include <curl/curl.h>

// Callback para escribir datos recibidos
struct WriteData
{
    std::string data;
};

// Tipo para funciones manejadoras de rutas
using RouteHandler = std::function<std::string(const std::string &)>;

class RequestHandler
{
private:
    std::map<std::string, RouteHandler> routes;

    // Callback para cURL para escribir datos
    static size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp)
    {
        size_t totalSize = size * nmemb;
        WriteData *writeData = static_cast<WriteData *>(userp);
        writeData->data.append(static_cast<char *>(contents), totalSize);
        return totalSize;
    }

public:
    RequestHandler();
    ~RequestHandler();

    void addRoute(const std::string &path, RouteHandler handler);
    std::string handleRequest(const std::string &method, const std::string &path, const std::string &body);
    void startServer(int port);
};

#endif