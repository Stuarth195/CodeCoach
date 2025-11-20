// runner.cpp (Windows / MinGW) - Updated Logic
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string>
#include <vector>
#include <chrono>
#include <fstream>
#include <filesystem>
#include <sstream>
#include <iostream>

#include "runner.h"
#include "json.hpp"

using json = nlohmann::json;
namespace fs = std::filesystem;
using namespace std::chrono;
using namespace runner;

// --- Utilería interna ---

static void writeFileAll(const std::string &path, const std::string &content) {
    std::ofstream ofs(path, std::ios::binary);
    ofs << content;
    ofs.close();
}

static std::string normalizeSpaces(const std::string &s) {
    std::istringstream iss(s);
    std::string token, out;
    bool first = true;
    while (iss >> token) {
        if (!first) out += " ";
        out += token;
        first = false;
    }
    return out;
}

// Genera el archivo completo inyectando el código del usuario y creando el main con las instancias
static std::string generate_full_source(const EvalRequest &req) {
    std::ostringstream src;
    
    // 1. Headers standard comunes
    src << "#include <iostream>\n";
    src << "#include <string>\n";
    src << "#include <vector>\n";
    src << "#include <algorithm>\n";
    src << "#include <cmath>\n";
    src << "#include <map>\n";
    src << "using namespace std;\n\n";

    // 2. Código del usuario (La función)
    src << "// --- User Code Start ---\n";
    src << req.user_code << "\n";
    src << "// --- User Code End ---\n\n";

    // 3. Main generado automáticamente
    src << "int main() {\n";
    
    // Iteramos por los tests para generar las llamadas
    // Usamos un delimitador para poder separar los outputs después
    for (const auto &test : req.tests) {
        std::string input_val = test.first;
        
        // Inyeccion directa: cout << nombre_funcion(input) << endl;
        // Se imprime un delimitador "###END_CASE###" para separar salidas
        src << "    try {\n";
        src << "        std::cout << " << req.function_name << "(" << input_val << ") << std::endl;\n";
        src << "    } catch(...) { std::cout << \"ERROR_RUNTIME\" << std::endl; }\n";
        // Delimitador explicito para parsear la salida luego
        // (Aunque endl ya separa por lineas, esto es mas seguro si la funcion imprime cosas extra)
        // Para simplificar segun el prompt, usaremos saltos de linea y parsearemos lineas.
    }

    src << "    return 0;\n";
    src << "}\n";

    return src.str();
}

// Ejecuta proceso y captura stdout
static bool run_process_capture(const std::string &cmdline, const std::string &workdir,
                                int timeout_s,
                                std::string &out_stdout,
                                int &exit_code)
{
    out_stdout.clear();
    exit_code = -1;

    SECURITY_ATTRIBUTES sa{};
    sa.nLength = sizeof(SECURITY_ATTRIBUTES);
    sa.bInheritHandle = TRUE;

    HANDLE hStdOutRead = NULL, hStdOutWrite = NULL;
    if (!CreatePipe(&hStdOutRead, &hStdOutWrite, &sa, 0)) return false;
    if (!SetHandleInformation(hStdOutRead, HANDLE_FLAG_INHERIT, 0)) return false;

    STARTUPINFOA si{};
    si.cb = sizeof(si);
    si.dwFlags |= STARTF_USESTDHANDLES;
    si.hStdInput = NULL; // No necesitamos stdin, todo está inyectado
    si.hStdOutput = hStdOutWrite;
    si.hStdError = hStdOutWrite; // Capturamos stderr en el mismo stream para ver errores

    PROCESS_INFORMATION pi{};
    std::string cmd = cmdline;
    char *cmdC = &cmd[0];

    BOOL created = CreateProcessA(NULL, cmdC, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL,
                                  workdir.empty() ? NULL : workdir.c_str(), &si, &pi);

    CloseHandle(hStdOutWrite); // Importante cerrar el lado de escritura del padre

    if (!created) {
        CloseHandle(hStdOutRead);
        return false;
    }

    // Esperar con timeout
    DWORD waitRes = WaitForSingleObject(pi.hProcess, (DWORD)timeout_s * 1000);
    bool timed_out = false;
    if (waitRes == WAIT_TIMEOUT) {
        timed_out = true;
        TerminateProcess(pi.hProcess, 1);
    }

    // Leer salida
    char buffer[4096];
    DWORD readBytes = 0;
    while(ReadFile(hStdOutRead, buffer, sizeof(buffer), &readBytes, NULL) && readBytes > 0) {
        out_stdout.append(buffer, buffer + readBytes);
    }

    DWORD dwExit = 0;
    if (GetExitCodeProcess(pi.hProcess, &dwExit)) {
        exit_code = timed_out ? -1 : static_cast<int>(dwExit);
    }

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    CloseHandle(hStdOutRead);

    return !timed_out;
}

static CompileResult compile_source_windows(const std::string &gppExe,
                                           const std::string &srcPath,
                                           const std::string &exePath)
{
    CompileResult cr;
    // g++ src -o exe
    std::string cmd = "\"" + gppExe + "\" -std=c++17 -O2 \"" + srcPath + "\" -o \"" + exePath + "\"";
    
    int exitcode = -1;
    bool ok = run_process_capture(cmd, fs::path(srcPath).parent_path().string(), 10, cr.stdout_str, exitcode);
    
    cr.exit_code = exitcode;
    cr.ok = (ok && exitcode == 0);
    // Si hay error de compilacion, suele salir en stdout/stderr capturado en stdout_str
    if(!cr.ok && cr.stdout_str.empty()) cr.stdout_str = "Error desconocido al compilar.";
    
    return cr;
}

// --- Implementación Principal ---

std::string runner::evaluate_submission(const std::string &jsonContent, const std::string &gpp_exe)
{
    json req;
    try {
        req = json::parse(jsonContent);
    } catch (...) {
        return json{{"status", "error"}, {"message", "JSON invalido"}}.dump();
    }

    // 1. Parsear y mapear datos
    EvalRequest r;
    r.submission_id = req.value("nombre", "guest");
    r.user_code = req.value("codigo", "");
    r.filename = "main.cpp";
    
    // Obtener nombre de la funcion del JSON o fallback
    if (req.contains("function_name") && !req["function_name"].is_null()) {
        r.function_name = req["function_name"].get<std::string>();
    } else if (req.contains("problem_title")) {
        // Fallback: asumir que el título del problema es el nombre de la funcion
        r.function_name = req["problem_title"].get<std::string>();
    } else {
        return json{{"status", "error"}, {"message", "Falta 'function_name' o 'problem_title'"}}.dump();
    }

    // Extraer inputs y outputs
    for (int i = 1; i <= 3; ++i) {
        std::string kIn = "input" + std::to_string(i);
        std::string kOut = "output_esperado" + std::to_string(i);
        
        if (req.contains(kIn) && !req[kIn].is_null()) {
            std::string inVal = req[kIn].get<std::string>();
            // IMPORTANTE: El input viene del JSON. Si la funcion espera un string, 
            // el input en el JSON debe tener comillas (ej: "\"hola\"") O el usuario debe enviarlo así.
            // Asumiremos que viene formateado para C++ o es un número.
            
            if (inVal != "NO_ENCONTRADO" && !inVal.empty()) {
                std::string expected = "";
                if (req.contains(kOut) && !req[kOut].is_null()) {
                    expected = req[kOut].get<std::string>();
                    if (expected == "NO_ENCONTRADO") expected = "";
                }
                r.tests.push_back({inVal, expected});
            }
        }
    }

    if (r.user_code.empty()) return json{{"status", "error"}, {"message", "Sin codigo"}}.dump();

    // 2. Crear entorno temporal
    std::string uniq = std::to_string(GetCurrentProcessId()) + "_" + std::to_string(GetTickCount64());
    fs::path workdir = fs::temp_directory_path() / ("cc_" + uniq);
    fs::create_directories(workdir);
    
    std::string srcPath = (workdir / "main.cpp").string();
    std::string exePath = (workdir / "program.exe").string();

    // 3. Generar código completo e inyectarlo
    std::string fullSource = generate_full_source(r);
    writeFileAll(srcPath, fullSource);

    // 4. Compilar
    CompileResult cr = compile_source_windows(gpp_exe, srcPath, exePath);
    
    json response;
    
    if (!cr.ok) {
        response["status"] = "compile_error";
        response["message"] = cr.stdout_str; // Mensaje directo del compilador
        fs::remove_all(workdir); // Limpieza
        return response.dump();
    }

    // 5. Ejecutar (una sola vez para todos los casos)
    std::string runOutput;
    int runExitCode;
    bool runOk = run_process_capture("\"" + exePath + "\"", workdir.string(), r.run_timeout_s, runOutput, runExitCode);

    // Limpieza inmediata
    fs::remove_all(workdir);

    if (!runOk) { // Timeout
        return json{{"status", "runtime_error"}, {"message", "Tiempo de ejecucion excedido"}}.dump();
    }
    if (runExitCode != 0) {
        return json{{"status", "runtime_error"}, {"message", "Error en tiempo de ejecucion (Exit code " + std::to_string(runExitCode) + ")"}}.dump();
    }

    // 6. Procesar salidas
    // Separamos el stdout por lineas. Cada linea corresponde a un test case (según nuestro main generado)
    std::vector<std::string> outputLines;
    std::istringstream iss(runOutput);
    std::string line;
    while (std::getline(iss, line)) {
        if(!line.empty() && line.back() == '\r') line.pop_back(); // Quitar CR en Windows
        if(!line.empty()) outputLines.push_back(line);
    }

    // Construir respuesta concisa
    json resultsArray = json::array();
    bool allPassed = true;

    for (size_t i = 0; i < r.tests.size(); ++i) {
        std::string actual = (i < outputLines.size()) ? outputLines[i] : "";
        std::string expected = r.tests[i].second;
        
        // Normalizar para comparación (quitar espacios extra si es necesario, o comparación exacta)
        bool passed = (normalizeSpaces(actual) == normalizeSpaces(expected));
        if (!passed) allPassed = false;

        // Estructura directa por test
        resultsArray.push_back({
            {"id", i + 1},
            {"input", r.tests[i].first},
            {"expected", expected},
            {"output", actual},
            {"passed", passed}
        });
    }

    response["status"] = allPassed ? "success" : "failed";
    response["results"] = resultsArray;
    
    // Mensaje general opcional muy corto
    response["message"] = allPassed ? "Todos los tests pasaron." : "Algunos tests fallaron.";

    return response.dump();
}
