// runner.h
#pragma once

// runner.h
// Lógica de compilación y ejecución AHORA CON DOCKER SANDBOX.
// Se integra con el formato JSON del proyecto CodeCoach.

#include <string>
#include <vector>
#include <cstdint>
#include <chrono>

namespace runner
{
    // Estructuras de datos para resultados internos
    struct TestResult
    {
        std::string id;
        bool passed = false;
        int exit_code = -1;
        bool timed_out = false;
        std::string stdout_str;
        std::string stderr_str;
    };

    struct EvaluationResult
    {
        std::string status;
        std::string summary;
        int passed_count;
        int total_tests;
        int score;
        bool problem_solved;
        std::string compilation_output;
        std::string execution_output;
        std::vector<std::pair<std::string, std::string>> test_details;
        std::vector<bool> test_passed;
        std::chrono::milliseconds execution_time;
    };

    struct CompileResult
    {
        bool ok = false;
        int exit_code = -1;
        bool timed_out = false;
        std::string stdout_str;
        std::string stderr_str;
    };

    struct EvalRequest
    {
        std::string submission_id;
        std::string user_code;                // Codigo del usuario (solo la funcion)
        std::string function_name;            // Nombre de la funcion a llamar (ej: "esPalindromo")
        std::string function_type = "string"; // ✅ NUEVO: Tipo de la función (valor por defecto: string)
        std::string filename;                 // Por defecto main.cpp

        int compile_timeout_s = 10;
        int run_timeout_s = 2;

        // Vector de pares (input_arg_code, expected_stdout)
        // Nota: input_arg_code se inyectará tal cual en el código C++.
        // Si es string debe venir con comillas desde el JSON o manejarse aqui.
        std::vector<std::pair<std::string, std::string>> tests;
    };

    // Declaración de generate_full_source
    std::string generate_full_source(const EvalRequest &req);

    // Funciones principales
    // Nota: gpp_exe se mantiene por compatibilidad, pero Docker usa su propio compilador interno.
    EvaluationResult evaluate_submission_detailed(const std::string &jsonContent, const std::string &gpp_exe = "g++");
    
    // Función simple de compilación (wrapper)
    std::string evaluate_submission(const std::string &jsonContent);

    // Helpers de JSON
    std::string evaluation_result_to_json(const EvaluationResult &res);
}