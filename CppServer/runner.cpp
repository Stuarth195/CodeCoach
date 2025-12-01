// runner.cpp - VERSIÓN DEFINITIVA: DOCKER SANDBOX + LOGICA IA COMPLETA
// Este archivo reemplaza completamente al runner antiguo.
// Mantiene toda la lógica de parsing y generación de código, pero usa Docker para ejecutar.

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string>
#include <vector>
#include <chrono>
#include <fstream>
#include <filesystem>
#include <sstream>
#include <iostream>
#include <array>   // Buffers
#include <memory>  // Punteros inteligentes
#include <cstdio>  // Pipes

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

    // Limpia espacios en blanco al inicio y final de un string
    std::string cleanString(const std::string &s)
    {
        size_t first = s.find_first_not_of(" \t\r\n");
        if (std::string::npos == first)
            return "";
        size_t last = s.find_last_not_of(" \t\r\n");
        return s.substr(first, (last - first + 1));
    }

    // Ejecuta un comando de sistema y captura su salida estándar (stdout)
    // Reemplaza a toda la lógica compleja de CreateProcess y Pipes de Windows.
    std::string exec_docker_cmd(const char* cmd) {
        std::array<char, 128> buffer;
        std::string result;
        
        // _popen crea un proceso hijo y abre un pipe hacia él de forma sencilla
        std::unique_ptr<FILE, decltype(&_pclose)> pipe(_popen(cmd, "r"), _pclose);
        
        if (!pipe) {
            return "ERROR_SYSTEM: No se pudo invocar Docker.";
        }
        
        // Leer la salida mientras haya datos
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
            result += buffer.data();
        }
        return result;
    }

    // ==========================================
    // SECCIÓN 2: GENERACIÓN DE CÓDIGO (LÓGICA CRÍTICA)
    // ==========================================
    // Aquí es donde reconstruimos las "líneas perdidas" de helpers.
    // Inyectamos código C++ dentro del archivo temporal para manejar inputs complejos.

    std::string generate_full_source(const EvalRequest &req)
    {
        std::ostringstream src;

        // 1. Headers necesarios
        src << "#include <iostream>\n";
        src << "#include <string>\n";
        src << "#include <sstream>\n";
        src << "#include <vector>\n";
        src << "#include <list>\n";
        src << "#include <map>\n";
        src << "#include <algorithm>\n";
        src << "#include <cmath>\n";
        src << "#include <iomanip>\n";
        src << "using namespace std;\n\n";

        // 2. Inyección del código del usuario
        src << "// --- CÓDIGO DEL USUARIO ---\n";
        src << req.user_code << "\n";
        src << "// --------------------------\n\n";

        // 3. HELPERS INYECTADOS (Para que el código compile bien con inputs complejos)
        
        // Helper: Convertir string "[1,2,3]" a vector<int>
        src << "vector<int> stringToVector(string s) {\n";
        src << "    vector<int> res;\n";
        src << "    if(s.size()<2) return res;\n";
        src << "    s = s.substr(1, s.size()-2);\n"; // Quitar corchetes
        src << "    stringstream ss(s);\n";
        src << "    string segment;\n";
        src << "    while(getline(ss, segment, ',')) {\n";
        src << "        try { res.push_back(stoi(segment)); } catch(...) {}\n";
        src << "    }\n";
        src << "    return res;\n";
        src << "}\n\n";

        // Helpers de Impresión (Sobrecargas para print_result)
        src << "// Helpers para imprimir cualquier tipo de dato\n";
        src << "void print_result(const string& res) { cout << res << endl; }\n";
        src << "void print_result(const char* res) { cout << res << endl; }\n";
        src << "void print_result(int res) { cout << res << endl; }\n";
        src << "void print_result(long long res) { cout << res << endl; }\n";
        src << "void print_result(double res) { cout << res << endl; }\n";
        src << "void print_result(float res) { cout << res << endl; }\n";
        src << "void print_result(bool res) { cout << (res ? \"1\" : \"0\") << endl; }\n";
        
        // Helper para imprimir vectores
        src << "template<typename T> void print_result(const vector<T>& v) {";
        src << "cout << \"[\"; for(size_t i=0; i<v.size(); ++i) { cout << v[i] << (i<v.size()-1?\",\":\"\"); } cout << \"]\" << endl; }\n\n";

        // 4. FUNCIÓN MAIN AUTOGENERADA
        src << "int main() {\n";
        
        // Generar llamadas para cada caso de prueba
        for (size_t i = 0; i < req.tests.size(); ++i) {
            std::string arg = req.tests[i].first;
            
            // Lógica simple de detección de tipos para inputs
            // Si el input empieza con '[', asumimos que es un vector y usamos el helper
            std::string call_arg = arg;
            if (!arg.empty() && arg[0] == '[') {
                call_arg = "stringToVector(\"" + arg + "\")";
            }
            
            src << "    try {\n";
            src << "        // Test Case " << i+1 << "\n";
            src << "        print_result(" << req.function_name << "(" << call_arg << "));\n";
            src << "    } catch (...) { cout << \"RUNTIME_ERROR\" << endl; }\n";
        }
        
        src << "    return 0;\n";
        src << "}\n";

        return src.str();
    }

    // ==========================================
    // SECCIÓN 3: PROCESO PRINCIPAL (EVALUACIÓN)
    // ==========================================

    EvaluationResult evaluate_submission_detailed(const std::string &jsonContent, const std::string &gpp_exe)
    {
        EvaluationResult result;
        EvalRequest req;
        
        // --- PASO 1: PARSEAR JSON (Recuperando toda la data) ---
        try {
            auto j = json::parse(jsonContent);
            
            // Campos obligatorios
            if (j.contains("codigo")) req.user_code = j["codigo"];
            
            // Nombre de función (con fallback para evitar errores)
            if (j.contains("function_name") && j["function_name"] != "NO_ENCONTRADO") 
                req.function_name = j["function_name"];
            else 
                req.function_name = "solve"; 
                
            if (j.contains("function_type")) req.function_type = j["function_type"];

            // Extraer casos de prueba (Inputs y Outputs esperados)
            if (j.contains("input1") && !j["input1"].get<std::string>().empty()) 
                req.tests.push_back({j["input1"], j.contains("output_esperado1") ? j["output_esperado1"] : ""});
            if (j.contains("input2") && !j["input2"].get<std::string>().empty()) 
                req.tests.push_back({j["input2"], j.contains("output_esperado2") ? j["output_esperado2"] : ""});
            if (j.contains("input3") && !j["input3"].get<std::string>().empty()) 
                req.tests.push_back({j["input3"], j.contains("output_esperado3") ? j["output_esperado3"] : ""});

        } catch (const std::exception &e) {
            result.status = "error";
            result.execution_output = std::string("Error parseando JSON: ") + e.what();
            return result;
        }

        // --- PASO 2: PREPARAR SANDBOX ---
        fs::path current_path = fs::current_path();
        fs::path temp_dir = current_path / "temp_sandbox";
        
        // Crear carpeta temporal
        if (!fs::exists(temp_dir)) fs::create_directory(temp_dir);

        // Definir ruta del archivo .cpp
        std::string filename = "solution.cpp";
        fs::path host_file_path = temp_dir / filename;

        // --- PASO 3: GENERAR ARCHIVO .CPP ---
        std::string full_code = generate_full_source(req);

        {
            std::ofstream out(host_file_path);
            if (!out) {
                result.status = "error";
                result.execution_output = "Error escribiendo archivo temporal en host.";
                return result;
            }
            out << full_code;
        }

        // --- PASO 4: EJECUCIÓN EN DOCKER ---
        
        // Obtener ruta absoluta para el montaje
        std::string abs_path = fs::absolute(temp_dir).string();
        
        // Construimos el comando Docker
        std::string docker_cmd = "docker run --rm --network none --memory=\"128m\" --cpus=\"0.5\" ";
        docker_cmd += "-v \"" + abs_path + ":/app\" "; // Montar volumen
        docker_cmd += "-w /app ";                       // Workdir
        docker_cmd += "frolvlad/alpine-gxx ";           // Imagen
        // Comando interno: compilar static y ejecutar
        docker_cmd += "sh -c \"g++ -static -O2 solution.cpp -o prog && ./prog\"";

        std::cout << "🐳 Docker Sandbox: " << docker_cmd << std::endl;

        auto start_time = high_resolution_clock::now();
        
        // Ejecutar y esperar respuesta
        std::string runOutput = exec_docker_cmd(docker_cmd.c_str());
        
        auto end_time = high_resolution_clock::now();
        result.execution_time = duration_cast<milliseconds>(end_time - start_time);

        // --- PASO 5: ANÁLISIS DE RESULTADOS ---
        
        // Verificar si Docker o GCC reportaron error
        if (runOutput.find("error:") != std::string::npos || runOutput.find("g++: error") != std::string::npos) {
            result.status = "compilation_error";
            result.compilation_output = runOutput;
            result.score = 0;
            result.problem_solved = false;
            // Rellenar con fallos para mantener consistencia
            for(size_t i=0; i<req.tests.size(); i++) result.test_passed.push_back(false);
            return result;
        }

        result.compilation_output = "Compilación exitosa (Container)";
        result.execution_output = runOutput;

        // Dividir la salida por líneas
        std::vector<std::string> lines;
        std::istringstream iss(runOutput);
        std::string line;
        while (std::getline(iss, line))
        {
            lines.push_back(cleanString(line));
        }

        // Comparar con OutputNormalizer
        json tests_result = json::array();
        int passed_count = 0;
        int total_tests = req.tests.size();

        for (int i = 0; i < total_tests; ++i)
        {
            std::string expected = cleanString(req.tests[i].second);
            std::string obtained = (i < lines.size()) ? lines[i] : "Sin salida / Runtime Error";
            std::string input_display = req.tests[i].first;

            // Usar la lógica avanzada de comparación (Arrays, Bools, etc.)
            bool passed = OutputNormalizer::compare(expected, obtained, req.function_type);
            
            if (passed) passed_count++;

            // Guardar detalles para la IA
            result.test_details.push_back({input_display, obtained});
            result.test_passed.push_back(passed);
        }

        // --- PASO 6: RESULTADO FINAL ---
        std::string summary = std::to_string(passed_count) + "/" + std::to_string(total_tests) + " Correctos";
        
        result.status = (passed_count == total_tests) ? "success" : "failed";
        result.summary = summary;
        result.passed_count = passed_count;
        result.total_tests = total_tests;
        result.score = (total_tests > 0) ? (passed_count * 100 / total_tests) : 0;
        result.problem_solved = (passed_count == total_tests);

        return result;
    }

    // Wrapper para compatibilidad simple
    std::string evaluate_submission(const std::string &jsonContent)
    {
        EvaluationResult res = evaluate_submission_detailed(jsonContent);
        return evaluation_result_to_json(res);
    }

    // Conversión a JSON final (Formato exacto para la GUI/IA)
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
        for(size_t i=0; i<res.test_details.size(); i++) {
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