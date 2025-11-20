// runner.cpp (Windows / MinGW)
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
#include "json.hpp" // Asegúrate de que este archivo esté accesible

using json = nlohmann::json;
namespace fs = std::filesystem;
using namespace std::chrono;
using namespace runner;

// Utilería interna
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

// Ejecuta un proceso capturando stdout/stderr con timeout (Win32 API)
static bool run_process_capture(const std::string &cmdline, const std::string &workdir,
                                const std::string &stdin_data,
                                int timeout_s,
                                std::string &out_stdout, std::string &out_stderr,
                                int &exit_code, bool &timed_out)
{
    out_stdout.clear(); out_stderr.clear();
    exit_code = -1;
    timed_out = false;

    SECURITY_ATTRIBUTES sa{};
    sa.nLength = sizeof(SECURITY_ATTRIBUTES);
    sa.bInheritHandle = TRUE;
    sa.lpSecurityDescriptor = NULL;

    HANDLE hStdOutRead = NULL, hStdOutWrite = NULL;
    HANDLE hStdErrRead = NULL, hStdErrWrite = NULL;
    HANDLE hStdInRead = NULL, hStdInWrite = NULL;

    if (!CreatePipe(&hStdOutRead, &hStdOutWrite, &sa, 0)) return false;
    if (!SetHandleInformation(hStdOutRead, HANDLE_FLAG_INHERIT, 0)) return false;
    if (!CreatePipe(&hStdErrRead, &hStdErrWrite, &sa, 0)) return false;
    if (!SetHandleInformation(hStdErrRead, HANDLE_FLAG_INHERIT, 0)) return false;
    if (!CreatePipe(&hStdInRead, &hStdInWrite, &sa, 0)) return false;
    if (!SetHandleInformation(hStdInWrite, HANDLE_FLAG_INHERIT, 0)) return false;

    STARTUPINFOA si{};
    PROCESS_INFORMATION pi{};
    si.cb = sizeof(si);
    si.dwFlags |= STARTF_USESTDHANDLES;
    si.hStdInput = hStdInRead;
    si.hStdOutput = hStdOutWrite;
    si.hStdError = hStdErrWrite;

    std::string cmd = cmdline;
    char *cmdC = &cmd[0]; // Mutable char* para CreateProcess

    BOOL created = CreateProcessA(NULL, cmdC, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL,
                                  workdir.empty() ? NULL : workdir.c_str(), &si, &pi);

    // Cerrar extremos de escritura en el padre para evitar bloqueos
    CloseHandle(hStdOutWrite);
    CloseHandle(hStdErrWrite);
    CloseHandle(hStdInRead);

    if (!created) {
        CloseHandle(hStdOutRead);
        CloseHandle(hStdErrRead);
        CloseHandle(hStdInWrite);
        return false;
    }

    // Escribir stdin al proceso hijo
    if (!stdin_data.empty()) {
        DWORD written = 0;
        WriteFile(hStdInWrite, stdin_data.data(), (DWORD)stdin_data.size(), &written, NULL);
    }
    CloseHandle(hStdInWrite); // Señal de EOF

    // Esperar finalización o timeout
    DWORD waitRes = WaitForSingleObject(pi.hProcess, (DWORD)timeout_s * 1000);
    if (waitRes == WAIT_TIMEOUT) {
        timed_out = true;
        TerminateProcess(pi.hProcess, 1);
        WaitForSingleObject(pi.hProcess, 1000);
    }

    // Leer salidas
    char buffer[4096];
    DWORD readBytes = 0;
    while(ReadFile(hStdOutRead, buffer, sizeof(buffer), &readBytes, NULL) && readBytes > 0) {
        out_stdout.append(buffer, buffer + readBytes);
    }
    while(ReadFile(hStdErrRead, buffer, sizeof(buffer), &readBytes, NULL) && readBytes > 0) {
        out_stderr.append(buffer, buffer + readBytes);
    }

    DWORD dwExit = 0;
    if (GetExitCodeProcess(pi.hProcess, &dwExit)) {
        exit_code = timed_out ? -1 : static_cast<int>(dwExit);
    }

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    CloseHandle(hStdOutRead);
    CloseHandle(hStdErrRead);

    return true;
}

static CompileResult compile_source_windows(const std::string &gppExe,
                                           const std::string &srcPath,
                                           const std::string &exePath,
                                           int compile_timeout_s)
{
    CompileResult cr;
    // Comando: g++ -std=c++17 -O2 "src" -o "exe"
    std::ostringstream cmd;
    cmd << "\"" << gppExe << "\" -std=c++17 -O2 \"" << srcPath << "\" -o \"" << exePath << "\"";
    
    std::string out, err;
    int exitcode = -1;
    bool timed_out = false;
    // Ejecutar compilación en el directorio del archivo fuente
    bool ok = run_process_capture(cmd.str(), fs::path(srcPath).parent_path().string(), "", compile_timeout_s, out, err, exitcode, timed_out);
    
    cr.stdout_str = out;
    cr.stderr_str = err;
    cr.exit_code = exitcode;
    cr.timed_out = timed_out;
    cr.ok = (ok && !timed_out && exitcode == 0);
    return cr;
}

static TestResult run_test_windows(const std::string &exePath,
                                   const std::string &stdin_data,
                                   const std::string &expected,
                                   int run_timeout_s,
                                   const std::string &compare_mode,
                                   const std::string &workdir)
{
    TestResult tr;
    std::string cmd = "\"" + exePath + "\"";
    
    bool ok = run_process_capture(cmd, workdir, stdin_data, run_timeout_s, tr.stdout_str, tr.stderr_str, tr.exit_code, tr.timed_out);

    if (!tr.timed_out && tr.exit_code == 0) {
        // Lógica de comparación
        if (expected == "NO_ENCONTRADO" || expected.empty()) {
             // Si no hay output esperado, consideramos que pasó si no crasheó
             tr.passed = true;
        } else {
            if (compare_mode == "exact") 
                tr.passed = (tr.stdout_str == expected);
            else 
                tr.passed = (normalizeSpaces(tr.stdout_str) == normalizeSpaces(expected));
        }
    } else {
        tr.passed = false;
    }
    return tr;
}

// Implementación principal expuesta
std::string runner::evaluate_submission(const std::string &jsonContent, const std::string &gpp_exe)
{
    auto tstart = high_resolution_clock::now();
    json req;
    try {
        req = json::parse(jsonContent);
    } catch (std::exception &e) {
        json errj = {{"status","error"}, {"message","Invalid JSON"}, {"detail", e.what()}};
        return errj.dump(2);
    }

    // 1. Parsear Request mapeando los campos de CodeCoach (Format)
    EvalRequest r;
    r.submission_id = req.value("nombre", "guest"); // Usamos el nombre como ID simple
    r.source = req.value("codigo", "");
    r.filename = "main.cpp";
    
    // Extraer inputs y outputs esperados (input1..3, output_esperado1..3)
    for (int i = 1; i <= 3; ++i) {
        std::string kIn = "input" + std::to_string(i);
        std::string kOut = "output_esperado" + std::to_string(i);
        
        if (req.contains(kIn) && !req[kIn].is_null()) {
            std::string inVal = req[kIn].get<std::string>();
            std::string outVal = "";
            if (req.contains(kOut) && !req[kOut].is_null()) {
                outVal = req[kOut].get<std::string>();
            }
            
            // Ignorar si dice "NO_ENCONTRADO" (logica de format.cpp)
            if (inVal != "NO_ENCONTRADO" && !inVal.empty()) {
                if (outVal == "NO_ENCONTRADO") outVal = "";
                r.tests.push_back({inVal, outVal});
            }
        }
    }

    // Validar que haya código
    if (r.source.empty() || r.source == "NO_ENCONTRADO") {
        json errj = {{"status","error"}, {"message","No code provided"}};
        return errj.dump();
    }

    // 2. Configurar entorno temporal
    std::string tmpBase;
    char tmpPathBuf[MAX_PATH];
    if (GetTempPathA(MAX_PATH, tmpPathBuf) == 0) tmpBase = ".\\";
    else tmpBase = std::string(tmpPathBuf);
    
    // ID único para carpeta
    std::string uniq = std::to_string(GetCurrentProcessId()) + "-" + std::to_string(GetTickCount64());
    fs::path workdir = fs::path(tmpBase) / ("cc_run_" + uniq);
    fs::create_directories(workdir);
    
    std::string srcPath = (workdir / r.filename).string();
    std::string exePath = (workdir / "program.exe").string();

    writeFileAll(srcPath, r.source);

    // 3. Compilar
    CompileResult cr = compile_source_windows(gpp_exe, srcPath, exePath, r.compile_timeout_s);

    json out;
    out["compile"] = {
        {"ok", cr.ok},
        {"exit_code", cr.exit_code},
        {"timeout", cr.timed_out},
        {"stdout", cr.stdout_str},
        {"stderr", cr.stderr_str}
    };

    if (!cr.ok) {
        out["status"] = "compile_error";
        out["message"] = "Error de compilación";
        out["results"] = json::array();
        try { fs::remove_all(workdir); } catch(...) {}
        return out.dump(2);
    }

    // 4. Ejecutar Tests
    json results = json::array();
    int passedCount = 0;
    
    for (size_t i = 0; i < r.tests.size(); ++i) {
        TestResult tr = run_test_windows(exePath, r.tests[i].first, r.tests[i].second, 
                                         r.run_timeout_s, r.compare_mode, workdir.string());
        if (tr.passed) ++passedCount;
        
        results.push_back({
            {"id", i+1},
            {"passed", tr.passed},
            {"stdout", tr.stdout_str},
            {"stderr", tr.stderr_str},
            {"exit_code", tr.exit_code},
            {"timeout", tr.timed_out},
            {"expected", r.tests[i].second}
        });
    }

    out["results"] = results;
    
    // Determinar estado global
    if (r.tests.empty()) {
        out["status"] = "success";
        out["message"] = "Compilación exitosa (sin tests definidos)";
    } else {
        std::ostringstream msg;
        msg << "Estado: " << ((passedCount == (int)r.tests.size()) ? "Código correcto" : "Código incorrecto") << "\n";
        for (size_t i = 0; i < r.tests.size(); ++i) {
            msg << "Input: " << r.tests[i].first
                << " | Output esperado: " << r.tests[i].second
                << " | Output obtenido: " << out["results"][i]["stdout"].get<std::string>() << "\n";
        }
        out["status"] = (passedCount == (int)r.tests.size()) ? "success" : "failed";
        out["message"] = msg.str();
    }

    auto tend = high_resolution_clock::now();
    out["elapsed_ms"] = duration_cast<milliseconds>(tend - tstart).count();

    // Limpieza
    try { fs::remove_all(workdir); } catch(...) {}

    return out.dump(2);
}