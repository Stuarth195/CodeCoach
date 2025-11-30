// runner.cpp - Updated for concise output and comparison WITH DOCKER SANDBOX
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string>
#include <vector>
#include <chrono>
#include <fstream>
#include <filesystem>
#include <sstream>
#include <iostream>
#include <array>   // Nuevo para buffers
#include <memory>  // Nuevo para punteros inteligentes
#include <cstdio>  // Nuevo para pipe

#include "runner.h"
#include "json.hpp"
#include "OutputNormalizer.h"

using json = nlohmann::json;
namespace fs = std::filesystem;
using namespace std::chrono;
using namespace runner;

namespace runner
{

    // --- HELPER PARA EJECUTAR COMANDOS (REEMPLAZO DE CREATEPROCESS) ---
    std::string exec_docker_cmd(const char* cmd) {
        std::array<char, 128> buffer;
        std::string result;
        // _popen abre un pipe para leer la salida del comando (stdout)
        std::unique_ptr<FILE, decltype(&_pclose)> pipe(_popen(cmd, "r"), _pclose);
        if (!pipe) {
            return "ERROR_SYSTEM: No se pudo invocar Docker.";
        }
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
            result += buffer.data();
        }
        return result;
    }

    // --- HELPER STRINGS ---
    std::string cleanString(const std::string &s)
    {
        size_t first = s.find_first_not_of(" \t\r\n");
        if (std::string::npos == first)
            return "";
        size_t last = s.find_last_not_of(" \t\r\n");
        return s.substr(first, (last - first + 1));
    }

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
        src << "using namespace std;\n\n";

        // 2. Código del usuario
        src << "// --- User Code ---\n";
        src << req.user_code << "\n";
        src << "// -----------------\n\n";

        // 3. HELPERS PARA CONVERSIÓN DE TIPOS
        src << "// Helper para convertir string a vector<int>\n";
        src << "vector<int> stringToVector(string s) {\n";
        src << "    vector<int> res;\n";
        src << "    if(s.size()<2) return res;\n";
        src << "    s = s.substr(1, s.size()-2);\n";
        src << "    stringstream ss(s);\n";
        src << "    string segment;\n";
        src << "    while(getline(ss, segment, ',')) {\n";
        src << "        try { res.push_back(stoi(segment)); } catch(...) {}\n";
        src << "    }\n";
        src << "    return res;\n";
        src << "}\n\n";

        src << "void print_result(const string& res) { cout << res << endl; }\n";
        src << "void print_result(int res) { cout << res << endl; }\n";
        src << "void print_result(bool res) { cout << (res ? \"1\" : \"0\") << endl; }\n";
        src << "void print_result(double res) { cout << res << endl; }\n";
        
        src << "template<typename T> void print_result(const vector<T>& v) {";
        src << "cout << \"[\"; for(size_t i=0; i<v.size(); ++i) { cout << v[i] << (i<v.size()-1?\",\":\"\"); } cout << \"]\" << endl; }\n\n";

        // 4. MAIN GENERADO
        src << "int main() {\n";
        
        for (size_t i = 0; i < req.tests.size(); ++i) {
            std::string arg = req.tests[i].first;
            
            // Detección simple si el input es un vector (empieza con [)
            // Si tu lógica requiere conversión compleja, mantén tu inyección actual.
            // Aquí asumimos que arg ya viene formateado para C++ (ej: "{1,2,3}" o "vector<int>{1,2}")
            // Si viene como string "[1,2]" desde JSON, hay que adaptarlo.
            // Para simplificar y respetar tu lógica actual, inyectamos directo.
            
            src << "    try {\n";
            // Nota: Se asume que req.function_name y los args son válidos
            src << "        print_result(" << req.function_name << "(" << arg << "));\n";
            src << "    } catch (...) { cout << \"RUNTIME_ERROR\" << endl; }\n";
        }
        
        src << "    return 0;\n";
        src << "}\n";

        return src.str();
    }

    EvaluationResult evaluate_submission_detailed(const std::string &jsonContent, const std::string &gpp_exe)
    {
        EvaluationResult result;
        EvalRequest req;
        
        // 1. Parsear JSON
        try {
            auto j = json::parse(jsonContent);
            if (j.contains("codigo")) req.user_code = j["codigo"];
            
            // Manejo de nombre de función con fallback
            if (j.contains("function_name") && j["function_name"] != "NO_ENCONTRADO") 
                req.function_name = j["function_name"];
            else 
                req.function_name = "solve"; // Nombre por defecto si falla
                
            if (j.contains("function_type")) req.function_type = j["function_type"];

            // Extraer inputs y outputs esperados
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

        // 2. Preparar entorno temporal
        // Usamos una carpeta local 'temp_sandbox'
        fs::path current_path = fs::current_path();
        fs::path temp_dir = current_path / "temp_sandbox";
        
        // Crear directorio si no existe (y limpiar errores previos si es necesario)
        if (!fs::exists(temp_dir)) fs::create_directory(temp_dir);

        // Nombre de archivo estandarizado para Docker
        std::string filename = "solution.cpp";
        fs::path host_file_path = temp_dir / filename;

        // 3. Generar el código fuente completo
        std::string full_code = generate_full_source(req);

        // Escribir archivo al disco
        {
            std::ofstream out(host_file_path);
            if (!out) {
                result.status = "error";
                result.execution_output = "Error escribiendo archivo temporal en host.";
                return result;
            }
            out << full_code;
        }

        // 4. EJECUCIÓN CON DOCKER (SANDBOX)
        // Construimos el comando.
        // -rm: Borra contenedor al salir.
        // --network none: Sin internet.
        // -v: Volumen. Mapea temp_dir (host) -> /app (container).
        // frolvlad/alpine-gxx: Imagen ligera.
        // sh -c: Ejecuta compilación Y ejecución en una línea.
        
        std::string abs_path = fs::absolute(temp_dir).string();
        
        // Comando Docker: Compila estáticamente y ejecuta
        // Usamos comillas escapadas para rutas de Windows
        std::string docker_cmd = "docker run --rm --network none --memory=\"128m\" --cpus=\"0.5\" ";
        docker_cmd += "-v \"" + abs_path + ":/app\" ";
        docker_cmd += "-w /app ";
        docker_cmd += "frolvlad/alpine-gxx ";
        docker_cmd += "sh -c \"g++ -static -O2 solution.cpp -o prog && ./prog\"";

        std::cout << "🐳 Ejecutando Docker: " << docker_cmd << std::endl;

        auto start_time = high_resolution_clock::now();
        
        // Ejecutar y capturar salida
        std::string runOutput = exec_docker_cmd(docker_cmd.c_str());
        
        auto end_time = high_resolution_clock::now();
        result.execution_time = duration_cast<milliseconds>(end_time - start_time);

        // Limpieza (Opcional: borrar el cpp generado)
        // fs::remove(host_file_path);

        // 5. Procesar Resultados (Misma lógica que antes, analizando stdout)
        // Docker retorna stdout + stderr mezclado en el pipe si hay errores de compilación
        // Verificamos si hubo error de compilación buscando palabras clave o si output está vacío
        
        if (runOutput.find("error:") != std::string::npos || runOutput.find("g++: error") != std::string::npos) {
            result.status = "compilation_error";
            result.compilation_output = runOutput;
            result.score = 0;
            return result;
        }

        // Si llegamos aquí, asumimos que corrió (o intentó correr)
        result.compilation_output = "Compilación exitosa (en Docker)";
        result.execution_output = runOutput;

        // Parsear líneas de salida para comparar con tests
        std::vector<std::string> lines;
        std::istringstream iss(runOutput);
        std::string line;
        while (std::getline(iss, line))
        {
            lines.push_back(cleanString(line));
        }

        json tests_result = json::array();
        int passed_count = 0;
        int total_tests = req.tests.size();

        for (int i = 0; i < total_tests; ++i)
        {
            // Usamos OutputNormalizer para comparar (Tu clase existente)
            std::string expected = cleanString(req.tests[i].second);
            std::string obtained = (i < lines.size()) ? lines[i] : "Sin salida"; // Prevenir crash si output es corto
            std::string input_display = req.tests[i].first;

            // Usar el normalizador para comparar inteligentemente
            bool passed = OutputNormalizer::compare(expected, obtained, req.function_type);
            
            if (passed) passed_count++;

            tests_result.push_back({
                {"test_id", i + 1},
                {"input", input_display},
                {"expected", expected},
                {"obtained", obtained},
                {"passed", passed}
            });
            
            result.test_passed.push_back(passed);
            result.test_details.push_back({input_display, obtained});
        }

        // 6. Construcción de Respuesta Concisa
        std::string summary = std::to_string(passed_count) + "/" + std::to_string(total_tests) + " Correctos";
        
        result.status = (passed_count == total_tests) ? "success" : "failed";
        result.summary = summary;
        result.passed_count = passed_count;
        result.total_tests = total_tests;
        result.score = (total_tests > 0) ? (passed_count * 100 / total_tests) : 0;
        result.problem_solved = (passed_count == total_tests);

        return result;
    }

    // Wrapper simple (Mantiene compatibilidad con main.cpp)
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
        
        // Añadir detalles de tests
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