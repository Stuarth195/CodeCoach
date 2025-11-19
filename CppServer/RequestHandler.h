// RequestHandler.h
#ifndef REQUESTHANDLER_H
#define REQUESTHANDLER_H

#include <iostream>
#include <string>
#include <functional>
#include <map>
#include <sstream>

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
    RequestHandler();
    ~RequestHandler();

    void addRoute(const std::string &path, std::function<std::string(const std::string &)> handler);
    void startServer(int port);
};

#endif