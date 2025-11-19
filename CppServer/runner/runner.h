#pragma once

// runner.h
// Runner para Windows (MinGW): compila y ejecuta código C++ enviado en JSON,
// corre 3 tests y devuelve JSON con resultados.
//
// Dependencias:
// - nlohmann::json (header-only) -> include/nlohmann/json.hpp
// - Compilador g++ (MinGW) disponible en PATH.

#include <string>
#include <vector>
#include <cstdint>

namespace runner {

struct TestResult {
    std::string id;
    bool passed = false;
    int exit_code = -1;     // exit code (>=0) o -1 si terminado por kill/timeout
    bool timed_out = false;
    std::string stdout_str;
    std::string stderr_str;
};

struct CompileResult {
    bool ok = false;
    int exit_code = -1;
    bool timed_out = false;
    std::string stdout_str;
    std::string stderr_str;
};

struct EvalRequest {
    std::string submission_id;
    std::string source; // código C++
    std::string filename; // nombre a usar: e.g., main.cpp
    int compile_timeout_s = 10;
    int run_timeout_s = 2;
    uint64_t memory_limit_bytes = 128ULL * 1024 * 1024;
    std::string compare_mode = "normalize"; // "exact" | "normalize"
    // tests: vector of pairs (stdin, expected)
    std::vector<std::pair<std::string,std::string>> tests;
};

struct EvalResult {
    std::string submission_id;
    CompileResult compile;
    std::vector<TestResult> results;
    long elapsed_ms = 0;
};

// Lee JSON desde 'jsonPath' y ejecuta la evaluación.
// Retorna JSON-string con los resultados (serializado).
std::string evaluate_from_json_file(const std::string &jsonPath, const std::string &gpp_exe = "g++");

} // namespace runner