// format.cpp
#include "format.h"
#include <iostream>
#include <vector>
#include <algorithm> // min

Format::Format(const std::string &json_str)
{
    try
    {
        json j = json::parse(json_str);
        inicializarDesdeJson(j);
    }
    catch (const json::parse_error &e)
    {
        std::cerr << "❌ Error parseando JSON: " << e.what() << std::endl;
        nombre = "ERROR_PARSE";
        codigo = "";
    }
}

Format::Format(const json &json_obj)
{
    inicializarDesdeJson(json_obj);
}

void Format::inicializarDesdeJson(const json &j)
{
    nombre = extraerCampo(j, "nombre");
    codigo = extraerCampo(j, "codigo");
    problem_title = extraerCampo(j, "problem_title");
    // Intentamos obtener function_name, si no existe usamos problem_title como fallback
    // o asumimos que viene en el campo "function_name"
    function_name = extraerCampo(j, "function_name");
    if (function_name == "NO_ENCONTRADO") {
        // Fallback opcional: usar problem_title si el JSON no trae function_name explicitamente
        // Se asume que problem_title no tiene espacios si se usa como funcion
        function_name = problem_title; 
    }
    difficulty = extraerCampo(j, "difficulty");
    input1 = extraerCampo(j, "input1");
    input2 = extraerCampo(j, "input2");
    input3 = extraerCampo(j, "input3");
    output_esperado1 = extraerCampo(j, "output_esperado1");
    output_esperado2 = extraerCampo(j, "output_esperado2");
    output_esperado3 = extraerCampo(j, "output_esperado3");
}

std::string Format::getNombre() const { return nombre; }
std::string Format::getCodigo() const { return codigo; }
std::string Format::getProblemTitle() const { return problem_title; }
std::string Format::getFunctionName() const { return function_name; }
std::string Format::getDifficulty() const { return difficulty; }
std::string Format::getInput1() const { return input1; }
std::string Format::getInput2() const { return input2; }
std::string Format::getInput3() const { return input3; }
std::string Format::getOutputEsperado1() const { return output_esperado1; }
std::string Format::getOutputEsperado2() const { return output_esperado2; }
std::string Format::getOutputEsperado3() const { return output_esperado3; }

std::string Format::getCodigoParaCompilar() const { return codigo; }

std::vector<std::string> Format::getInputs() const
{
    std::vector<std::string> inputs;
    if (!input1.empty() && input1 != "NO_ENCONTRADO") inputs.push_back(input1);
    if (!input2.empty() && input2 != "NO_ENCONTRADO") inputs.push_back(input2);
    if (!input3.empty() && input3 != "NO_ENCONTRADO") inputs.push_back(input3);
    return inputs;
}

std::vector<std::string> Format::getOutputsEsperados() const
{
    std::vector<std::string> outputs;
    if (!output_esperado1.empty() && output_esperado1 != "NO_ENCONTRADO") outputs.push_back(output_esperado1);
    if (!output_esperado2.empty() && output_esperado2 != "NO_ENCONTRADO") outputs.push_back(output_esperado2);
    if (!output_esperado3.empty() && output_esperado3 != "NO_ENCONTRADO") outputs.push_back(output_esperado3);
    return outputs;
}

bool Format::esValido() const
{
    return !nombre.empty() && nombre != "NO_ENCONTRADO" &&
           !codigo.empty() && codigo != "NO_ENCONTRADO" && nombre != "ERROR_PARSE";
}

void Format::mostrarInformacion() const
{
    std::cout << "🔍 INFORMACIÓN DEL FORMULARIO:" << std::endl;
    std::cout << "   👤 Usuario: " << nombre << std::endl;
    std::cout << "   📝 Problema: " << problem_title << std::endl;
    std::cout << "   📄 Código (snippet): " << codigo.substr(0, std::min(50, (int)codigo.length())) << "..." << std::endl;
    std::cout << "   ✅ Válido: " << (esValido() ? "Si" : "No") << std::endl;
    std::cout << "   Funcion: " << function_name << std::endl;
}

std::string Format::extraerCampo(const json &j, const std::string &campo)
{
    try
    {
        if (j.contains(campo) && !j[campo].is_null())
        {
            if (j[campo].is_string()) return j[campo].get<std::string>();
            else return j[campo].dump();
        }
    }
    catch (...) { }
    return "NO_ENCONTRADO";
}