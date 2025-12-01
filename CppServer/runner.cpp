// runner.cpp - VERSIÓN FINAL: LOGICA TUYA + FIX DOCKER + EXCEPTION

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string>
#include <vector>
#include <chrono>
#include <fstream>
#include <filesystem>
#include <sstream>
#include <iostream>
#include <array>
#include <memory>
#include <cstdio>
#include <algorithm> // Necesario para replace

#include "runner.h"
#include "json.hpp"
#include "OutputNormalizer.h"

using json = nlohmann::json;
namespace fs = std::filesystem;
using namespace std::chrono;
using namespace runner;

namespace runner
{
    // ==========================================
    // SECCIÓN 1: HERRAMIENTAS AUXILIARES
    // ==========================================

    std::string cleanString(const std::string &s)
    {
        size_t first = s.find_first_not_of(" \t\r\n");
        if (std::string::npos == first)
            return "";
        size_t last = s.find_last_not_of(" \t\r\n");
        return s.substr(first, (last - first + 1));
    }

    // Corrige rutas de Windows (C:\...) a formato Docker (C:/...)
    std::string sanitizePathForDocker(const std::string &path)
    {
        std::string p = path;
        std::replace(p.begin(), p.end(), '\\', '/');
        return p;
    }

    // Ejecuta comando y captura TODO (stdout + stderr)
    std::string exec_docker_cmd(const char *cmd)
    {
        std::array<char, 128> buffer;
        std::string result;
        std::unique_ptr<FILE, decltype(&_pclose)> pipe(_popen(cmd, "r"), _pclose);
        if (!pipe)
            return "ERROR_SYSTEM: No se pudo invocar Docker.";
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr)
        {
            result += buffer.data();
        }
        return result;
    }

    // ==========================================
    // SECCIÓN 2: GENERACIÓN DE CÓDIGO (TU VERSIÓN MEJORADA)
    // ==========================================

    std::string generate_full_source(const EvalRequest &req)
    {
        std::ostringstream src;

        // 1. Headers básicos
        src << "#include <iostream>\n";
        src << "#include <string>\n";
        src << "#include <sstream>\n";
        src << "#include <vector>\n";
        src << "#include <list>\n";
        src << "#include <algorithm>\n";
        src << "#include <exception>\n"; // <--- AGREGADO: Necesario para que compile el catch
        src << "using namespace std;\n\n";

        // 2. Código del usuario
        src << "// --- User Code ---\n";
        src << req.user_code << "\n";
        src << "// -----------------\n\n";

        // 3. HELPERS PARA CONVERSIÓN DE TIPOS
        src << "// Helper para convertir string a vector<int>\n";
        src << "vector<int> stringToVector(const string& str) {\n";
        src << "    vector<int> result;\n";
        src << "    if (str.empty() || str == \"[]\") return result;\n";
        src << "    string clean_str = str.substr(1, str.length() - 2);\n";
        src << "    stringstream ss(clean_str);\n";
        src << "    string token;\n";
        src << "    while (getline(ss, token, ',')) {\n";
        src << "        result.push_back(stoi(token));\n";
        src << "    }\n";
        src << "    return result;\n";
        src << "}\n\n";

        src << "// Helper para convertir vector<int> a string\n";
        src << "string vectorToString(const vector<int>& vec) {\n";
        src << "    string result = \"[\";\n";
        src << "    for (size_t i = 0; i < vec.size(); i++) {\n";
        src << "        result += to_string(vec[i]);\n";
        src << "        if (i < vec.size() - 1) result += \",\";\n";
        src << "    }\n";
        src << "    result += \"]\";\n";
        src << "    return result;\n";
        src << "}\n\n";

        src << "// Helper para convertir string a list<int>\n";
        src << "list<int> stringToList(const string& str) {\n";
        src << "    list<int> result;\n";
        src << "    if (str.empty() || str == \"[]\") return result;\n";
        src << "    string clean_str = str.substr(1, str.length() - 2);\n";
        src << "    stringstream ss(clean_str);\n";
        src << "    string token;\n";
        src << "    while (getline(ss, token, ',')) {\n";
        src << "        result.push_back(stoi(token));\n";
        src << "    }\n";
        src << "    return result;\n";
        src << "}\n\n";

        src << "// Helper para convertir list<int> a string\n";
        src << "string listToString(const list<int>& lst) {\n";
        src << "    string result = \"[\";\n";
        src << "    string valStr;\n"; // Corrección menor para evitar errores de compilador
        src << "    bool first = true;\n";
        src << "    for (int val : lst) {\n";
        src << "        if (!first) result += \",\";\n";
        src << "        result += to_string(val);\n";
        src << "        first = false;\n";
        src << "    }\n";
        src << "    result += \"]\";\n";
        src << "    return result;\n";
        src << "}\n\n";

        // 4. MAIN INTELIGENTE
        src << "int main() {\n";

        std::string user_code = req.user_code;

        // Detectar tipo de parámetro
        bool receives_int = user_code.find("(int ") != std::string::npos || user_code.find("(int)") != std::string::npos || user_code.find("(int&") != std::string::npos || user_code.find("(int x") != std::string::npos || user_code.find("(int n") != std::string::npos;
        bool receives_string = user_code.find("(string ") != std::string::npos || user_code.find("(string)") != std::string::npos || user_code.find("(string&") != std::string::npos || user_code.find("(std::string") != std::string::npos || user_code.find("(string s") != std::string::npos;
        bool receives_bool = user_code.find("(bool ") != std::string::npos || user_code.find("(bool)") != std::string::npos;
        bool receives_double = user_code.find("(double ") != std::string::npos || user_code.find("(double)") != std::string::npos;
        bool receives_char = user_code.find("(char ") != std::string::npos || user_code.find("(char)") != std::string::npos;
        bool receives_vector = user_code.find("(vector<int>") != std::string::npos || user_code.find("(vector<int>&") != std::string::npos || user_code.find("(vector<int> ") != std::string::npos;
        bool receives_list = user_code.find("(list<int>") != std::string::npos || user_code.find("(list<int>&") != std::string::npos || user_code.find("(list<int> ") != std::string::npos;

        if (!receives_int && !receives_string && !receives_bool && !receives_double && !receives_char && !receives_vector && !receives_list)
        {
            receives_string = true;
        }

        for (size_t i = 0; i < req.tests.size(); i++)
        {
            const auto &test = req.tests[i];
            std::string input_val = test.first;

            src << "    \n";
            src << "    // Test " << (i + 1) << ": " << input_val << "\n";
            src << "    try {\n";

            // GENERACIÓN DE CÓDIGO SEGÚN TIPO DE PARÁMETRO
            if (receives_string)
            {
                src << "        string input_val = \"" << input_val << "\";\n";
            }
            else if (receives_int)
            {
                src << "        int input_val = " << input_val << ";\n";
            }
            else if (receives_double)
            {
                src << "        double input_val = " << input_val << ";\n";
            }
            else if (receives_bool)
            {
                std::string bool_value = "false";
                if (input_val == "1" || input_val == "true" || input_val == "True")
                    bool_value = "true";
                src << "        bool input_val = " << bool_value << ";\n";
            }
            else if (receives_char)
            {
                if (input_val.length() > 1 && input_val[0] == '\"' && input_val[input_val.length() - 1] == '\"')
                    src << "        char input_val = '" << input_val.substr(1, input_val.length() - 2) << "';\n";
                else
                    src << "        char input_val = '" << input_val << "';\n";
            }
            else if (receives_vector)
            {
                src << "        vector<int> input_val = stringToVector(\"" << input_val << "\");\n";
            }
            else if (receives_list)
            {
                src << "        list<int> input_val = stringToList(\"" << input_val << "\");\n";
            }

            // GENERACIÓN DE LLAMADA Y OUTPUT
            if (req.function_type == "bool")
            {
                src << "        bool result = " << req.function_name << "(input_val);\n";
                src << "        cout << (result ? \"1\" : \"0\") << endl;\n";
            }
            else if (req.function_type == "int")
            {
                src << "        int result = " << req.function_name << "(input_val);\n";
                src << "        cout << result << endl;\n";
            }
            else if (req.function_type == "double")
            {
                src << "        double result = " << req.function_name << "(input_val);\n";
                src << "        cout << result << endl;\n";
            }
            else if (req.function_type == "string")
            {
                src << "        string result = " << req.function_name << "(input_val);\n";
                src << "        cout << result << endl;\n";
            }
            else if (req.function_type == "char")
            {
                src << "        char result = " << req.function_name << "(input_val);\n";
                src << "        cout << result << endl;\n";
            }
            else if (req.function_type == "array" || req.function_type == "vector")
            {
                src << "        vector<int> result = " << req.function_name << "(input_val);\n";
                src << "        cout << vectorToString(result) << endl;\n";
            }
            else if (req.function_type == "list")
            {
                src << "        list<int> result = " << req.function_name << "(input_val);\n";
                src << "        cout << listToString(result) << endl;\n";
            }
            else
            {
                src << "        auto result = " << req.function_name << "(input_val);\n";
                src << "        cout << result << endl;\n";
            }

            src << "    } catch(const exception& e) { \n";
            src << "        cout << \"ERROR_RUNTIME: \" << e.what() << endl; \n";
            src << "    } catch(...) { \n";
            src << "        cout << \"ERROR_RUNTIME_UNKNOWN\" << endl; \n";
            src << "    }\n";
        }

        src << "    return 0;\n";
        src << "}\n";

        return src.str();
    }

    // ==========================================
    // SECCIÓN 3: PROCESO PRINCIPAL
    // ==========================================
    // ==========================================
    // SECCIÓN 3: PROCESO PRINCIPAL (CORREGIDO)
    // ==========================================
    EvaluationResult evaluate_submission_detailed(const std::string &jsonContent, const std::string &gpp_exe)
    {
        EvaluationResult result;
        EvalRequest req;

        // 1. Parseo JSON
        try
        {
            auto j = json::parse(jsonContent);
            if (j.contains("codigo"))
                req.user_code = j["codigo"];
            req.function_name = (j.contains("function_name") && j["function_name"] != "NO_ENCONTRADO") ? j["function_name"].get<std::string>() : "solve";
            if (j.contains("function_type"))
                req.function_type = j["function_type"];

            if (j.contains("input1") && !j["input1"].get<std::string>().empty())
                req.tests.push_back({j["input1"], j.contains("output_esperado1") ? j["output_esperado1"] : ""});
            if (j.contains("input2") && !j["input2"].get<std::string>().empty())
                req.tests.push_back({j["input2"], j.contains("output_esperado2") ? j["output_esperado2"] : ""});
            if (j.contains("input3") && !j["input3"].get<std::string>().empty())
                req.tests.push_back({j["input3"], j.contains("output_esperado3") ? j["output_esperado3"] : ""});
        }
        catch (const std::exception &e)
        {
            result.status = "error";
            result.execution_output = std::string("Error parseando JSON: ") + e.what();
            return result;
        }

        // 2. Preparar Sandbox
        fs::path current_path = fs::current_path();
        fs::path temp_dir = current_path / "temp_sandbox";
        if (!fs::exists(temp_dir))
            fs::create_directory(temp_dir);

        std::string filename = "solution.cpp";
        fs::path host_file_path = temp_dir / filename;

        std::string full_code = generate_full_source(req);
        {
            std::ofstream out(host_file_path);
            if (!out)
            {
                result.status = "error";
                result.execution_output = "Error escribiendo archivo temporal en host.";
                return result;
            }
            out << full_code;
        }

        // 3. Ejecucion Docker
        std::string abs_path = fs::absolute(temp_dir).string();
        std::string docker_path = sanitizePathForDocker(abs_path);

        // Comando Docker con timeout corregido (sin -t) y redireccion de errores (2>&1)
        std::string docker_cmd = "docker run --rm --network none --memory=\"128m\" --cpus=\"0.5\" ";
        docker_cmd += "-v \"" + docker_path + ":/app\" ";
        docker_cmd += "-w /app ";
        docker_cmd += "frolvlad/alpine-gxx ";
        docker_cmd += "sh -c \"g++ -static -O2 solution.cpp -o prog 2>&1 && timeout 3 ./prog 2>&1\"";

        std::cout << "Docker Sandbox: " << docker_cmd << std::endl;

        auto start_time = high_resolution_clock::now();
        std::string runOutput = exec_docker_cmd(docker_cmd.c_str());
        auto end_time = high_resolution_clock::now();
        result.execution_time = duration_cast<milliseconds>(end_time - start_time);

        // 4. Analisis de Errores (Deteccion de texto crudo)

        // Error de compilacion detectado por palabras clave de GCC
        if (runOutput.find("error:") != std::string::npos ||
            runOutput.find("g++: error") != std::string::npos ||
            runOutput.find("fatal error:") != std::string::npos ||
            runOutput.find("No such file") != std::string::npos)
        {
            result.status = "compilation_error";
            // Guardamos el mensaje EXACTO de GCC para que la IA lo lea
            result.compilation_output = runOutput;
            result.score = 0;
            result.problem_solved = false;
            for (size_t i = 0; i < req.tests.size(); i++)
                result.test_passed.push_back(false);
            return result;
        }

        // Error de tiempo (Timeout)
        if (runOutput.find("Terminated") != std::string::npos ||
            runOutput.find("command terminated") != std::string::npos)
        {
            result.status = "time_limit_exceeded";
            result.summary = "Tiempo limite excedido.";
            result.execution_output = runOutput;
            result.score = 0;
            result.problem_solved = false;
            return result;
        }

        // Ejecucion completada (analisis de salida)
        result.compilation_output = "Compilacion exitosa";
        result.execution_output = runOutput;

        std::vector<std::string> lines;
        std::istringstream iss(runOutput);
        std::string line;
        while (std::getline(iss, line))
        {
            lines.push_back(cleanString(line));
        }

        int passed_count = 0;
        int total_tests = req.tests.size();

        for (int i = 0; i < total_tests; ++i)
        {
            std::string expected = cleanString(req.tests[i].second);
            std::string obtained = (i < lines.size()) ? lines[i] : "Sin salida / Error";
            std::string input_display = req.tests[i].first;

            // Deteccion de excepciones C++ capturadas por el try/catch generado
            if (obtained.find("ERROR_RUNTIME") != std::string::npos)
            {
                result.status = "runtime_error";
                result.summary = obtained; // Contiene el mensaje de la excepcion (what)
            }

            bool passed = OutputNormalizer::compare(expected, obtained, req.function_type);
            if (passed)
                passed_count++;

            result.test_details.push_back({input_display, obtained});
            result.test_passed.push_back(passed);
        }

        if (result.status.empty())
        {
            result.status = (passed_count == total_tests) ? "success" : "failed";
        }

        result.summary = std::to_string(passed_count) + "/" + std::to_string(total_tests) + " Correctos";
        result.passed_count = passed_count;
        result.total_tests = total_tests;
        result.score = (total_tests > 0) ? (passed_count * 100 / total_tests) : 0;
        result.problem_solved = (passed_count == total_tests);

        return result;
    }

    std::string evaluate_submission(const std::string &jsonContent)
    {
        EvaluationResult res = evaluate_submission_detailed(jsonContent);
        return evaluation_result_to_json(res);
    }

    std::string evaluation_result_to_json(const EvaluationResult &res)
    {
        json j;
        j["status"] = res.status;
        j["summary"] = res.summary;
        j["passed_count"] = res.passed_count;
        j["total_tests"] = res.total_tests;
        j["score"] = res.score;
        j["problem_solved"] = res.problem_solved;
        j["compilation_output"] = res.compilation_output;
        j["execution_output"] = res.execution_output;

        json tests_array = json::array();
        for (size_t i = 0; i < res.test_details.size(); i++)
        {
            json t;
            t["input"] = res.test_details[i].first;
            t["obtained"] = res.test_details[i].second;
            t["passed"] = (i < res.test_passed.size()) ? res.test_passed[i] : false;
            tests_array.push_back(t);
        }
        j["tests"] = tests_array;
        j["execution_time_ms"] = res.execution_time.count();

        return j.dump();
    }
}
