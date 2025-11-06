#include "CodeExecutor.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <cstdlib>
#include <filesystem>
#include <chrono>
#include <thread>

#ifdef _WIN32
#include <windows.h>
#include <process.h>
#else
#include <unistd.h>
#include <sys/wait.h>
#endif

CodeExecutor::CodeExecutor()
{
    // Crear directorio temporal único
    tempDirectory = "temp_code_" + std::to_string(time(nullptr));
    std::filesystem::create_directory(tempDirectory);
}

CodeExecutor::~CodeExecutor()
{
    // Limpiar directorio temporal
    try
    {
        std::filesystem::remove_all(tempDirectory);
    }
    catch (...)
    {
        // Ignorar errores de limpieza
    }
}

std::string CodeExecutor::generateSourceFile(const std::string &code)
{
    std::string sourcePath = tempDirectory + "/solution.cpp";
    std::ofstream sourceFile(sourcePath);

    if (!sourceFile.is_open())
    {
        throw std::runtime_error("No se pudo crear archivo fuente");
    }

    // Escribir el código del usuario
    sourceFile << code;
    sourceFile.close();

    return sourcePath;
}

bool CodeExecutor::compileCode(const std::string &sourcePath, const std::string &executablePath)
{
    // Comando de compilación para MSVC
    std::string compileCommand = "cl /EHsc /Fe\"" + executablePath + "\" \"" + sourcePath + "\" >nul 2>&1";

    int result = system(compileCommand.c_str());
    return result == 0;
}

std::string CodeExecutor::executeCode(const std::string &executablePath, const std::string &input)
{
    std::string command = "\"" + executablePath + "\"";
    std::string fullCommand = "echo " + input + " | " + command;

    FILE *pipe = _popen(fullCommand.c_str(), "r");
    if (!pipe)
    {
        return "ERROR: No se pudo ejecutar el programa";
    }

    char buffer[128];
    std::string result = "";
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr)
    {
        result += buffer;
    }

    _pclose(pipe);
    return cleanOutput(result);
}

std::string CodeExecutor::cleanOutput(const std::string &output)
{
    std::string cleaned = output;

    // Eliminar espacios y newlines al final
    while (!cleaned.empty() &&
           (cleaned.back() == '\n' || cleaned.back() == '\r' || cleaned.back() == ' '))
    {
        cleaned.pop_back();
    }

    return cleaned;
}

TestResult CodeExecutor::runTestCase(const std::string &executablePath, const TestCase &testCase)
{
    TestResult result;
    result.input_raw = testCase.input_raw;
    result.expected_output_raw = testCase.expected_output_raw;

    try
    {
        result.actual_output = executeCode(executablePath, testCase.input_raw);
        result.passed = (result.actual_output == testCase.expected_output_raw);

        if (result.passed)
        {
            result.status_message = "✅ PASÓ";
        }
        else
        {
            result.status_message = "❌ FALLÓ - Esperado: " + testCase.expected_output_raw +
                                    ", Obtenido: " + result.actual_output;
        }
    }
    catch (const std::exception &e)
    {
        result.actual_output = "ERROR: " + std::string(e.what());
        result.passed = false;
        result.status_message = "💥 ERROR: " + std::string(e.what());
    }

    return result;
}

EvaluationResponse CodeExecutor::evaluateCode(const EvaluationRequest &request)
{
    EvaluationResponse response;
    response.problem_title = request.problem_title;
    response.user_code = request.user_code;
    response.total_cases = request.test_cases.size();
    response.passed_cases = 0;
    response.failed_cases = 0;

    try
    {
        // 1. Generar archivo fuente
        std::string sourcePath = generateSourceFile(request.user_code);
        std::string executablePath = tempDirectory + "/solution.exe";

        // 2. Compilar código
        if (!compileCode(sourcePath, executablePath))
        {
            throw std::runtime_error("Error de compilación. Revisa tu código C++.");
        }

        // 3. Ejecutar casos de prueba
        for (const auto &testCase : request.test_cases)
        {
            TestResult testResult = runTestCase(executablePath, testCase);
            response.test_results.push_back(testResult);

            if (testResult.passed)
            {
                response.passed_cases++;
            }
            else
            {
                response.failed_cases++;
            }
        }

        // 4. Generar resumen
        std::stringstream summary;
        summary << "Resultados: " << response.passed_cases << " de " << response.total_cases << " casos pasaron";
        response.summary = summary.str();
    }
    catch (const std::exception &e)
    {
        response.summary = "Error durante la evaluación: " + std::string(e.what());
        response.failed_cases = response.total_cases;
    }

    return response;
}