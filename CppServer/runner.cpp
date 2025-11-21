// runner.cpp - Updated for concise output and comparison
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

static void writeFileAll(const std::string &path, const std::string &content)
{
    std::ofstream ofs(path, std::ios::binary);
    ofs << content;
    ofs.close();
}

// Normaliza strings para comparar (quita espacios al inicio/final y saltos de linea)
static std::string cleanString(const std::string &s)
{
    size_t first = s.find_first_not_of(" \t\r\n");
    if (std::string::npos == first)
        return "";
    size_t last = s.find_last_not_of(" \t\r\n");
    return s.substr(first, (last - first + 1));
}

// Genera el archivo completo inyectando el código del usuario
static std::string generate_full_source(const EvalRequest &req)
{
    std::ostringstream src;

    // 1. Headers comunes
    src << "#include <iostream>\n";
    src << "#include <string>\n";
    src << "#include <vector>\n";
    src << "#include <algorithm>\n";
    src << "#include <cmath>\n";
    src << "#include <map>\n";
    src << "using namespace std;\n\n";

    // 2. Código del usuario (Función)
    src << "// --- User Code ---\n";
    src << req.user_code << "\n";
    src << "// -----------------\n\n";

    // 3. Main generado: Ejecuta cada input e imprime el resultado en una línea nueva
    src << "int main() {\n";
    for (const auto &test : req.tests)
    {
        std::string input_val = test.first;
        src << "    try {\n";
        // Imprime delimitador para asegurar que leemos lineas vacias si la respuesta es vacia
        src << "        cout << " << req.function_name << "(" << input_val << ") << endl;\n";
        src << "    } catch(...) { cout << \"ERROR_RUNTIME\" << endl; }\n";
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
    if (!CreatePipe(&hStdOutRead, &hStdOutWrite, &sa, 0))
        return false;
    if (!SetHandleInformation(hStdOutRead, HANDLE_FLAG_INHERIT, 0))
        return false;

    STARTUPINFOA si{};
    si.cb = sizeof(si);
    si.dwFlags |= STARTF_USESTDHANDLES;
    si.hStdOutput = hStdOutWrite;
    si.hStdError = hStdOutWrite; // Capturamos errores en el mismo stream

    PROCESS_INFORMATION pi{};
    std::string cmd = cmdline;

    BOOL created = CreateProcessA(NULL, &cmd[0], NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL,
                                  workdir.empty() ? NULL : workdir.c_str(), &si, &pi);

    CloseHandle(hStdOutWrite);

    if (!created)
    {
        CloseHandle(hStdOutRead);
        return false;
    }

    DWORD waitRes = WaitForSingleObject(pi.hProcess, (DWORD)timeout_s * 1000);
    bool timed_out = false;
    if (waitRes == WAIT_TIMEOUT)
    {
        timed_out = true;
        TerminateProcess(pi.hProcess, 1);
    }

    char buffer[4096];
    DWORD readBytes = 0;
    while (ReadFile(hStdOutRead, buffer, sizeof(buffer), &readBytes, NULL) && readBytes > 0)
    {
        out_stdout.append(buffer, buffer + readBytes);
    }

    DWORD dwExit = 0;
    if (GetExitCodeProcess(pi.hProcess, &dwExit))
    {
        exit_code = timed_out ? -1 : static_cast<int>(dwExit);
    }

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    CloseHandle(hStdOutRead);

    return !timed_out;
}

static CompileResult compile_source_windows(const std::string &gppExe, const std::string &srcPath, const std::string &exePath)
{
    CompileResult cr;
    // Comando de compilación
    std::string cmd = "\"" + gppExe + "\" -std=c++17 -O2 \"" + srcPath + "\" -o \"" + exePath + "\"";

    int exitcode = -1;
    bool ok = run_process_capture(cmd, fs::path(srcPath).parent_path().string(), 10, cr.stdout_str, exitcode);

    cr.exit_code = exitcode;
    cr.ok = (ok && exitcode == 0);
    if (!cr.ok && cr.stdout_str.empty())
        cr.stdout_str = "Error desconocido al compilar.";
    return cr;
}

// --- Función Principal de Evaluación ---
EvaluationResult runner::evaluate_submission_detailed(const std::string &jsonContent, const std::string &gpp_exe)
{
    EvaluationResult result;
    auto start_time = std::chrono::high_resolution_clock::now();

    // Parse JSON y preparar request (similar a evaluate_submission existente)
    json req_json;
    try
    {
        req_json = json::parse(jsonContent);
    }
    catch (...)
    {
        result.status = "error";
        result.summary = "JSON inválido";
        return result;
    }

    EvalRequest r;
    r.submission_id = req_json.value("nombre", "user");
    r.user_code = req_json.value("codigo", "");

    // Obtener inputs y outputs
    for (int i = 1; i <= 3; ++i)
    {
        std::string kIn = "input" + std::to_string(i);
        std::string kOut = "output_esperado" + std::to_string(i);

        if (req_json.contains(kIn) && !req_json[kIn].is_null())
        {
            std::string inVal = req_json[kIn].get<std::string>();
            if (inVal != "NO_ENCONTRADO" && !inVal.empty())
            {
                std::string outVal = "";
                if (req_json.contains(kOut) && !req_json[kOut].is_null())
                {
                    outVal = req_json[kOut].get<std::string>();
                }
                r.tests.push_back({inVal, outVal});
            }
        }
    }

    // Configurar nombre de función
    if (req_json.contains("function_name"))
        r.function_name = req_json["function_name"].get<std::string>();
    else if (req_json.contains("problem_title"))
        r.function_name = req_json["problem_title"].get<std::string>();
    else
    {
        result.status = "error";
        result.summary = "Falta el nombre de la función";
        return result;
    }

    if (r.user_code.empty())
    {
        result.status = "error";
        result.summary = "Código vacío";
        return result;
    }

    result.total_tests = r.tests.size();

    // Crear entorno temporal y compilar
    std::string uniq = std::to_string(GetCurrentProcessId()) + "_" + std::to_string(GetTickCount64());
    fs::path workdir = fs::temp_directory_path() / ("cc_" + uniq);
    fs::create_directories(workdir);

    std::string srcPath = (workdir / "main.cpp").string();
    std::string exePath = (workdir / "program.exe").string();

    writeFileAll(srcPath, generate_full_source(r));
    CompileResult cr = compile_source_windows(gpp_exe, srcPath, exePath);
    result.compilation_output = cr.stdout_str;

    if (!cr.ok)
    {
        result.status = "compile_error";
        result.summary = "Error de compilación";
        result.passed_count = 0;
        result.score = 0;
        result.problem_solved = false;
        fs::remove_all(workdir);
        return result;
    }

    // Ejecutar y medir tiempo
    std::string runOutput;
    int runExitCode;
    bool runOk = run_process_capture("\"" + exePath + "\"", workdir.string(),
                                     r.run_timeout_s, runOutput, runExitCode);

    auto end_time = std::chrono::high_resolution_clock::now();
    result.execution_time = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    result.execution_output = runOutput;

    fs::remove_all(workdir);

    if (!runOk)
    {
        result.status = "runtime_error";
        result.summary = "Timeout en ejecución";
        result.passed_count = 0;
        result.score = 0;
        result.problem_solved = false;
        return result;
    }

    // Procesar resultados y calcular puntaje
    std::vector<std::string> lines;
    std::istringstream iss(runOutput);
    std::string line;
    while (std::getline(iss, line))
    {
        lines.push_back(cleanString(line));
    }

    result.passed_count = 0;
    int puntos_por_prueba = 10;

    for (int i = 0; i < result.total_tests; ++i)
    {
        std::string expected = cleanString(r.tests[i].second);
        std::string obtained = (i < lines.size()) ? lines[i] : "Sin salida";
        std::string input_display = r.tests[i].first;

        bool passed = (expected == obtained);
        result.test_passed.push_back(passed);
        result.test_details.push_back({input_display, obtained});

        if (passed)
        {
            result.passed_count++;
        }
    }

    // Calcular resultados finales
    result.score = result.passed_count * puntos_por_prueba;
    result.problem_solved = (result.passed_count == result.total_tests);
    result.status = result.problem_solved ? "success" : "failed";
    result.summary = std::to_string(result.passed_count) + "/" +
                     std::to_string(result.total_tests) + " Pruebas Correctas";

    return result;
}

std::string runner::evaluation_result_to_json(const EvaluationResult &result)
{
    json j;

    j["status"] = result.status;
    j["summary"] = result.summary;
    j["passed_count"] = result.passed_count;
    j["total_tests"] = result.total_tests;
    j["score"] = result.score;
    j["problem_solved"] = result.problem_solved;
    j["compilation_output"] = result.compilation_output;
    j["execution_output"] = result.execution_output;
    j["execution_time_ms"] = result.execution_time.count();

    json tests_array = json::array();
    for (size_t i = 0; i < result.test_details.size(); ++i)
    {
        tests_array.push_back({{"test_id", i + 1},
                               {"input", result.test_details[i].first},
                               {"obtained", result.test_details[i].second},
                               {"passed", result.test_passed[i]}});
    }
    j["tests"] = tests_array;

    return j.dump();
}

std::string runner::evaluate_submission(const std::string &jsonContent, const std::string &gpp_exe)
{
    json req_json;
    try
    {
        req_json = json::parse(jsonContent);
    }
    catch (...)
    {
        return json{{"status", "error"}, {"message", "JSON invalido"}}.dump();
    }

    // 1. Preparar Request
    EvalRequest r;
    r.submission_id = req_json.value("nombre", "user");
    r.user_code = req_json.value("codigo", "");

    // Obtener inputs y outputs esperados (Solo los 3 casos)
    // Se asume que vienen como input1, input2, input3 y output_esperado1...
    for (int i = 1; i <= 3; ++i)
    {
        std::string kIn = "input" + std::to_string(i);
        std::string kOut = "output_esperado" + std::to_string(i);

        if (req_json.contains(kIn) && !req_json[kIn].is_null())
        {
            std::string inVal = req_json[kIn].get<std::string>();
            if (inVal != "NO_ENCONTRADO" && !inVal.empty())
            {
                std::string outVal = "";
                if (req_json.contains(kOut) && !req_json[kOut].is_null())
                {
                    outVal = req_json[kOut].get<std::string>();
                }
                r.tests.push_back({inVal, outVal});
            }
        }
    }

    // Nombre de la función a ejecutar
    if (req_json.contains("function_name"))
        r.function_name = req_json["function_name"].get<std::string>();
    else if (req_json.contains("problem_title"))
        r.function_name = req_json["problem_title"].get<std::string>(); // Fallback
    else
        return json{{"status", "error"}, {"message", "Falta el nombre de la funcion"}}.dump();

    if (r.user_code.empty())
        return json{{"status", "error"}, {"message", "Codigo vacio"}}.dump();

    // 2. Crear entorno temporal
    std::string uniq = std::to_string(GetCurrentProcessId()) + "_" + std::to_string(GetTickCount64());
    fs::path workdir = fs::temp_directory_path() / ("cc_" + uniq);
    fs::create_directories(workdir);

    std::string srcPath = (workdir / "main.cpp").string();
    std::string exePath = (workdir / "program.exe").string();

    // 3. Inyección de código y Compilación
    writeFileAll(srcPath, generate_full_source(r));
    CompileResult cr = compile_source_windows(gpp_exe, srcPath, exePath);

    if (!cr.ok)
    {
        fs::remove_all(workdir);
        return json{
            {"status", "compile_error"},
            {"message", "Error de Compilacion"},
            {"details", cr.stdout_str}}
            .dump();
    }

    // 4. Ejecución (Una sola vez para los 3 inputs inyectados)
    std::string runOutput;
    int runExitCode;
    bool runOk = run_process_capture("\"" + exePath + "\"", workdir.string(), r.run_timeout_s, runOutput, runExitCode);
    fs::remove_all(workdir);

    if (!runOk)
        return json{{"status", "runtime_error"}, {"message", "Timeout"}}.dump();

    // 5. Procesar Resultados
    std::vector<std::string> lines;
    std::istringstream iss(runOutput);
    std::string line;
    while (std::getline(iss, line))
    {
        lines.push_back(cleanString(line));
    }

    json tests_result = json::array();
    int passed_count = 0;
    int total_tests = r.tests.size();

    for (int i = 0; i < total_tests; ++i)
    {
        std::string expected = cleanString(r.tests[i].second);
        std::string obtained = (i < lines.size()) ? lines[i] : "Sin salida";
        std::string input_display = r.tests[i].first;

        bool passed = (expected == obtained);
        if (passed)
            passed_count++;

        tests_result.push_back({{"test_id", i + 1},
                                {"input", input_display},
                                {"expected", expected},
                                {"obtained", obtained},
                                {"passed", passed}});
    }

    // 6. Construcción de Respuesta Concisa
    std::string summary = std::to_string(passed_count) + "/" + std::to_string(total_tests) + " Pruebas Correctas";
    std::string status = (passed_count == total_tests) ? "success" : "failed";

    return json{
        {"status", status},
        {"summary", summary},
        {"tests", tests_result}}
        .dump();
}