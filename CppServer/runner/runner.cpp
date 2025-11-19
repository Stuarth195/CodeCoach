// runner.cpp (Windows / MinGW)
// Implementación rústica del runner usando Win32 APIs:
// - lee JSON desde archivo
// - escribe source.cpp en workdir temporal
// - compila con g++ (CreateProcess, captura stdout/stderr)
// - si compila, ejecuta binario 3 veces (cada test) con timeout
// - produce JSON con resultados usando nlohmann::json
//
// Requisitos:
// - nlohmann::json.hpp en include path (CppServer/include/nlohmann/json.hpp)
// - Compilador g++ (MinGW) en PATH

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string>
#include <vector>
#include <chrono>
#include <fstream>
#include <filesystem>
#include <sstream>
#include <iostream>

#include "../runner/runner.h"
#include "../include/nlohmann/json.hpp"

using json = nlohmann::json;
namespace fs = std::filesystem;
using namespace std::chrono;
using namespace runner;

static std::string readFileAll(const std::string &path) {
    std::ifstream ifs(path, std::ios::binary);
    if (!ifs) return "";
    std::ostringstream ss;
    ss << ifs.rdbuf();
    return ss.str();
}

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

// Helper: create process with redirected pipes, returns exit_code and outputs, with timeout (seconds).
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

    // CreateProcess requires mutable char*
    std::string cmd = cmdline;
    char *cmdC = &cmd[0];

    BOOL created = CreateProcessA(NULL, cmdC, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL,
                                  workdir.empty() ? NULL : workdir.c_str(), &si, &pi);

    // Close handles we don't need in parent
    CloseHandle(hStdOutWrite);
    CloseHandle(hStdErrWrite);
    CloseHandle(hStdInRead);

    if (!created) {
        // cleanup remaining handles
        CloseHandle(hStdOutRead);
        CloseHandle(hStdErrRead);
        CloseHandle(hStdInWrite);
        return false;
    }

    // Write stdin if any
    if (!stdin_data.empty()) {
        DWORD written = 0;
        WriteFile(hStdInWrite, stdin_data.data(), (DWORD)stdin_data.size(), &written, NULL);
    }
    CloseHandle(hStdInWrite); // signal EOF to child

    // Wait for process with timeout
    DWORD waitRes = WaitForSingleObject(pi.hProcess, (DWORD)timeout_s * 1000);
    if (waitRes == WAIT_TIMEOUT) {
        // timeout: terminate
        timed_out = true;
        TerminateProcess(pi.hProcess, 1);
        // wait a bit
        WaitForSingleObject(pi.hProcess, 2000);
    }

    // Read stdout/stderr
    char buffer[4096];
    DWORD readBytes = 0;
    for (;;) {
        BOOL ok = ReadFile(hStdOutRead, buffer, sizeof(buffer), &readBytes, NULL);
        if (!ok || readBytes == 0) break;
        out_stdout.append(buffer, buffer + readBytes);
    }
    for (;;) {
        BOOL ok = ReadFile(hStdErrRead, buffer, sizeof(buffer), &readBytes, NULL);
        if (!ok || readBytes == 0) break;
        out_stderr.append(buffer, buffer + readBytes);
    }

    // Get exit code
    DWORD dwExit = 0;
    if (GetExitCodeProcess(pi.hProcess, &dwExit)) {
        if (!timed_out) exit_code = static_cast<int>(dwExit);
        else exit_code = -1;
    } else {
        exit_code = -1;
    }

    // cleanup
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    CloseHandle(hStdOutRead);
    CloseHandle(hStdErrRead);

    return true;
}

// Compile source.cpp into exe_path using g++ (assume g++ on PATH)
static CompileResult compile_source_windows(const std::string &gppExe,
                                           const std::string &srcPath,
                                           const std::string &exePath,
                                           int compile_timeout_s)
{
    CompileResult cr;
    // Build command line: g++ -std=c++17 -O2 "srcPath" -o "exePath"
    std::ostringstream cmd;
    cmd << "\"" << gppExe << "\" -std=c++17 -O2 \"" << srcPath << "\" -o \"" << exePath << "\"";
    std::string out, err;
    int exitcode = -1;
    bool timed_out = false;
    bool ok = run_process_capture(cmd.str(), fs::path(srcPath).parent_path().string(), "", compile_timeout_s, out, err, exitcode, timed_out);
    cr.stdout_str = out;
    cr.stderr_str = err;
    cr.exit_code = exitcode;
    cr.timed_out = timed_out;
    cr.ok = (ok && !timed_out && exitcode == 0);
    return cr;
}

// Run a single test
static TestResult run_test_windows(const std::string &exePath,
                                   const std::string &stdin_data,
                                   const std::string &expected,
                                   int run_timeout_s,
                                   uint64_t memory_limit_bytes,
                                   const std::string &compare_mode,
                                   const std::string &workdir)
{
    TestResult tr;
    tr.passed = false;
    tr.exit_code = -1;

    std::string cmd = "\"" + exePath + "\"";

    std::string out, err;
    int exitcode = -1;
    bool timed_out = false;

    bool ok = run_process_capture(cmd, workdir, stdin_data, run_timeout_s, out, err, exitcode, timed_out);

    tr.stdout_str = out;
    tr.stderr_str = err;
    tr.timed_out = timed_out;
    tr.exit_code = exitcode;
    if (!timed_out && exitcode == 0) {
        bool match = false;
        if (compare_mode == "exact") match = (tr.stdout_str == expected);
        else match = (normalizeSpaces(tr.stdout_str) == normalizeSpaces(expected));
        tr.passed = match;
    } else {
        tr.passed = false;
    }

    return tr;
}

// Main evaluation: read json file, produce result JSON string
std::string runner::evaluate_from_json_file(const std::string &jsonPath, const std::string &gpp_exe)
{
    auto tstart = high_resolution_clock::now();
    std::string body = readFileAll(jsonPath);
    json req;
    try {
        req = json::parse(body);
    } catch (std::exception &e) {
        json errj = {
            {"status","error"},
            {"message","invalid json"},
            {"detail", e.what()}
        };
        return errj.dump(2);
    }

    EvalRequest r;
    r.submission_id = req.value("submission_id", "");
    // legacy key 'codigo' used by PyLogic; fallback to 'source'
    r.source = req.value("codigo", req.value("source", ""));
    r.filename = req.value("filename", "main.cpp");
    r.compile_timeout_s = req.value("compile_timeout_s", 10);
    r.run_timeout_s = req.value("run_timeout_s", 2);
    r.memory_limit_bytes = req.value("memory_limit_bytes", 128ULL * 1024 * 1024);
    r.compare_mode = req.value("compare_mode", "normalize");

    // Collect tests: prefer tests array, else fallback to input1..3 format
    if (req.contains("tests") && req["tests"].is_array()) {
        for (auto &t : req["tests"]) {
            std::string sin = t.value("stdin", "");
            std::string exp = t.value("expected", "");
            r.tests.push_back({sin, exp});
        }
    } else {
        for (int i = 1; i <= 3; ++i) {
            std::string ik = "input" + std::to_string(i);
            std::string ok = "output_esperado" + std::to_string(i);
            std::string sin = req.value(ik, "");
            std::string exp = req.value(ok, "");
            r.tests.push_back({sin, exp});
        }
    }

    // Create workdir in TEMP
    std::string tmpBase;
    char tmpPathBuf[MAX_PATH];
    if (GetTempPathA(MAX_PATH, tmpPathBuf) == 0) tmpBase = ".\\";
    else tmpBase = std::string(tmpPathBuf);
    std::string uniq = std::to_string(GetCurrentProcessId()) + "-" + std::to_string(GetTickCount64());
    fs::path workdir = fs::path(tmpBase) / ("code-run-" + uniq);
    fs::create_directories(workdir);
    std::string srcPath = (workdir / r.filename).string();
    std::string exePath = (workdir / "a.exe").string();

    // Write source
    writeFileAll(srcPath, r.source);

    // compile
    CompileResult cr = compile_source_windows(gpp_exe, srcPath, exePath, r.compile_timeout_s);

    json out;
    out["submission_id"] = r.submission_id;
    out["compile"] = {
        {"ok", cr.ok},
        {"exit_code", cr.exit_code},
        {"timeout", cr.timed_out},
        {"stdout", cr.stdout_str},
        {"stderr", cr.stderr_str}
    };

    // if compile failed -> set status, cleanup and return
    if (!cr.ok) {
        out["status"] = "compile_error";
        out["message"] = "Compilation failed or timed out";
        out["results"] = json::array();
        try { fs::remove_all(workdir); } catch(...) {}
        auto tend = high_resolution_clock::now();
        out["elapsed_ms"] = duration_cast<milliseconds>(tend - tstart).count();
        return out.dump(2);
    }

    // run tests
    json results = json::array();
    int passedCount = 0;
    for (size_t i = 0; i < r.tests.size(); ++i) {
        TestResult tr = run_test_windows(exePath, r.tests[i].first, r.tests[i].second, r.run_timeout_s, r.memory_limit_bytes, r.compare_mode, workdir.string());
        if (tr.passed) ++passedCount;
        json jr = {
            {"id", std::to_string(i+1)},
            {"passed", tr.passed},
            {"exit_code", tr.exit_code},
            {"timeout", tr.timed_out},
            {"stdout", tr.stdout_str},
            {"stderr", tr.stderr_str}
        };
        results.push_back(jr);
    }

    out["results"] = results;
    if (passedCount == (int)r.tests.size()) {
        out["status"] = "success";
        out["message"] = "All tests passed";
    } else if (passedCount > 0) {
        out["status"] = "partial";
        out["message"] = "Some tests passed";
    } else {
        out["status"] = "failed";
        out["message"] = "No tests passed";
    }

    auto tend = high_resolution_clock::now();
    out["elapsed_ms"] = duration_cast<milliseconds>(tend - tstart).count();

    // cleanup
    try { fs::remove_all(workdir); } catch(...) {}

    return out.dump(2);
}