#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include "CodeExecutor.h"

#ifdef _WIN32
#define _WIN32_WINNT 0x0A00
#endif

#define CPPHTTPLIB_OPENSSL_SUPPORT
#include "httplib.h"
#include "json.hpp"

using json = nlohmann::json;
using namespace httplib;

// Convertir JSON a EvaluationRequest
EvaluationRequest jsonToEvaluationRequest(const json &j)
{
    EvaluationRequest request;

    request.problem_title = j["problem_title"];
    request.user_code = j["user_code"];

    for (const auto &testCase : j["test_cases"])
    {
        TestCase tc;
        tc.input_raw = testCase["input_raw"];
        tc.expected_output_raw = testCase["expected_output_raw"];
        request.test_cases.push_back(tc);
    }

    return request;
}

// Convertir EvaluationResponse a JSON
json evaluationResponseToJson(const EvaluationResponse &response)
{
    json j;

    j["problem_title"] = response.problem_title;
    j["user_code"] = response.user_code;
    j["summary"] = response.summary;
    j["total_cases"] = response.total_cases;
    j["passed_cases"] = response.passed_cases;
    j["failed_cases"] = response.failed_cases;

    json testResults = json::array();
    for (const auto &result : response.test_results)
    {
        json testResult;
        testResult["input_raw"] = result.input_raw;
        testResult["expected_output_raw"] = result.expected_output_raw;
        testResult["actual_output"] = result.actual_output;
        testResult["passed"] = result.passed;
        testResult["status_message"] = result.status_message;
        testResults.push_back(testResult);
    }
    j["test_results"] = testResults;

    return j;
}

int main()
{
    Server svr;
    CodeExecutor executor;

    std::cout << "🚀 Iniciando CodeCoach Server en http://localhost:5000" << std::endl;

    // Endpoint principal de evaluación
    svr.Post("/submit_evaluation", [&executor](const Request &req, Response &res)
             {
        std::cout << "📥 Recibida solicitud de evaluación..." << std::endl;
        
        try {
            // Parsear JSON de entrada
            json requestJson = json::parse(req.body);
            
            // Convertir a estructura de datos
            EvaluationRequest evalRequest = jsonToEvaluationRequest(requestJson);
            
            std::cout << "🔍 Evaluando problema: " << evalRequest.problem_title << std::endl;
            std::cout << "📝 Casos de prueba: " << evalRequest.test_cases.size() << std::endl;
            
            // Ejecutar evaluación
            EvaluationResponse evalResponse = executor.evaluateCode(evalRequest);
            
            // Convertir respuesta a JSON
            json responseJson = evaluationResponseToJson(evalResponse);
            
            // Configurar respuesta
            res.set_content(responseJson.dump(), "application/json");
            res.status = 200;
            
            std::cout << "✅ Evaluación completada: " << evalResponse.summary << std::endl;
            
        } catch (const std::exception& e) {
            std::cerr << "❌ Error procesando solicitud: " << e.what() << std::endl;
            
            json errorResponse = {
                {"error", "Error procesando la solicitud"},
                {"message", e.what()},
                {"status", "error"}
            };
            
            res.set_content(errorResponse.dump(), "application/json");
            res.status = 500;
        } });

    // Endpoint de salud
    svr.Get("/health", [](const Request &req, Response &res)
            {
        json health = {
            {"status", "ok"},
            {"service", "CodeCoach C++ Server"},
            {"timestamp", time(nullptr)}
        };
        res.set_content(health.dump(), "application/json"); });

    // Manejar errores CORS para desarrollo
    svr.Options(R"(.*)", [](const Request &req, Response &res)
                {
        res.set_header("Access-Control-Allow-Origin", "*");
        res.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        res.set_header("Access-Control-Allow-Headers", "Content-Type"); });

    // Configurar headers CORS
    svr.set_pre_routing_handler([](const Request &req, Response &res)
                                {
        res.set_header("Access-Control-Allow-Origin", "*");
        return Server::HandlerResponse::Unhandled; });

    // Iniciar servidor
    std::cout << "✅ Servidor listo. Esperando conexiones..." << std::endl;
    svr.listen("localhost", 5000);

    return 0;
}