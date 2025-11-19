// main.cpp - CON MANEJO DE JSON Y EJECUCIÓN DEL RUNNER
#include <iostream>
#include <string>
#include <fstream>
#include <filesystem>
#include <sstream>
#include <cstdio>

#include "RequestHandler.h"

namespace fs = std::filesystem;

static std::string write_temp_json(const std::string &body, const std::string &submission_id) {
    char tmpPathBuf[MAX_PATH];
    std::string tmpBase;
    if (GetTempPathA(MAX_PATH, tmpPathBuf) == 0) tmpBase = ".\\";
    else tmpBase = std::string(tmpPathBuf);

    std::string uniq = submission_id.empty() ? std::to_string(GetCurrentProcessId()) + "-" + std::to_string(GetTickCount64()) : submission_id;
    fs::path workdir = fs::path(tmpBase) / ("submission-" + uniq);
    fs::create_directories(workdir);
    fs::path jsonPath = workdir / "submission.json";

    std::ofstream ofs(jsonPath.string(), std::ios::binary);
    ofs << body;
    ofs.close();
    return jsonPath.string();
}

static std::string find_runner_exe() {
    // posibles ubicaciones relativas al ejecutable del servidor
    std::vector<std::string> candidates = {
        ".\\runner\\runner.exe",
        ".\\runner\\build\\runner.exe",
        "..\\CppServer\\runner\\runner.exe",
        ".\\runner.exe"
    };
    for (auto &c : candidates) {
        if (fs::exists(c)) return c;
    }
    // si no existe en relativas, devolver "runner.exe" y confiar en PATH
    return "runner.exe";
}

static std::string run_runner_and_capture(const std::string &runnerPath, const std::string &jsonPath) {
    // Construir comando con comillas
    std::string cmd = "\"" + runnerPath + "\" \"" + jsonPath + "\"";

    // Usamos _popen en Windows para capturar stdout de runner
#ifdef _WIN32
    FILE* pipe = _popen(cmd.c_str(), "r");
#else
    FILE* pipe = popen(cmd.c_str(), "r");
#endif
    if (!pipe) {
        // construir JSON de error simple
        return R"({"status":"error","message":"failed to run runner"})";
    }
    char buffer[4096];
    std::string result;
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        result += buffer;
    }
#ifdef _WIN32
    _pclose(pipe);
#else
    pclose(pipe);
#endif
    if (result.empty()) {
        return R"({"status":"error","message":"runner produced no output"})";
    }
    return result;
}

int main()
{
    std::cout << "🚀 Iniciando servidor C++ CodeCoach (HTTP REAL)..." << std::endl;
    std::cout << "📍 Escuchando en: http://localhost:5000" << std::endl;

    RequestHandler handler;

    // Endpoint principal para evaluación
    handler.addRoute("/submit_evaluation", [](const std::string &requestBody)
    {
        // Guardar el JSON recibido en un archivo temporal y ejecutar runner
        try {
            // Intentar extraer submission_id mínimo; si no está, usar random
            std::string submission_id = "";
            // Escribir JSON a archivo temporal
            std::string jsonPath = write_temp_json(requestBody, submission_id);

            // localizar runner.exe
            std::string runnerExe = find_runner_exe();

            std::cout << "📦 JSON guardado en: " << jsonPath << std::endl;
            std::cout << "▶️ Ejecutando runner: " << runnerExe << std::endl;

            std::string runnerOutput = run_runner_and_capture(runnerExe, jsonPath);

            std::cout << "📤 Runner output length: " << runnerOutput.size() << std::endl;

            // devolver exactamente lo que produjo runner (se espera JSON)
            return runnerOutput;
        } catch (std::exception &e) {
            std::ostringstream ss;
            ss << R"({"status":"error","message":"exception in server","detail":")" << e.what() << "\"}";
            return ss.str();
        }
    });

    handler.addRoute("/submit_code", [](const std::string &requestBody)
    {
        std::cout << "📥 Código simple recibido:" << std::endl;
        std::cout << requestBody << std::endl;
        return R"({
            "status": "success",
            "message": "Código recibido para compilación simple"
        })";
    });

    // Iniciar servidor
    handler.startServer(5000);

    return 0;
}