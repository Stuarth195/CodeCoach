#pragma once

// runner.h
// Lógica de compilación y ejecución para Windows (MinGW).
// Se integra con el formato JSON del proyecto CodeCoach.

#include <string>
#include <vector>
#include <cstdint>

namespace runner {

// Estructuras de datos para resultados internos
struct TestResult {
    std::string id;
    bool passed = false;
    int exit_code = -1;
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
    std::string source;     // Se mapea desde "codigo"
    std::string filename;   // Por defecto main.cpp
    int compile_timeout_s = 10;
    int run_timeout_s = 2;
    uint64_t memory_limit_bytes = 128ULL * 1024 * 1024;
    std::string compare_mode = "normalize"; 
    
    // Vector de pares (stdin, expected_stdout)
    std::vector<std::pair<std::string,std::string>> tests;
};

// Función principal integrada:
// Recibe el contenido JSON raw (requestBody), compila, ejecuta y retorna JSON string con resultados.
std::string evaluate_submission(const std::string &jsonContent, const std::string &gpp_exe = "g++");

} // namespace runner