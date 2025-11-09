// format.cpp
#include "format.h"
#include <iostream>

Format::Format(const std::string &json)
{
    // Parsear todos los campos del JSON
    nombre = extractField(json, "nombre");
    codigo = extractField(json, "codigo");
    problem_title = extractField(json, "problem_title");
    difficulty = extractField(json, "difficulty");
    input1 = extractField(json, "input1");
    input2 = extractField(json, "input2");
    input3 = extractField(json, "input3");
    output_esperado1 = extractField(json, "output_esperado1");
    output_esperado2 = extractField(json, "output_esperado2");
    output_esperado3 = extractField(json, "output_esperado3");
}

// Implementación de los getters
std::string Format::getNombre() const { return nombre; }
std::string Format::getCodigo() const { return codigo; }
std::string Format::getProblemTitle() const { return problem_title; }
std::string Format::getDifficulty() const { return difficulty; }
std::string Format::getInput1() const { return input1; }
std::string Format::getInput2() const { return input2; }
std::string Format::getInput3() const { return input3; }
std::string Format::getOutputEsperado1() const { return output_esperado1; }
std::string Format::getOutputEsperado2() const { return output_esperado2; }
std::string Format::getOutputEsperado3() const { return output_esperado3; }

void Format::mostrarInformacion() const
{
    std::cout << "🔍 INFORMACIÓN DEL FORMULARIO:" << std::endl;
    std::cout << "   👤 Usuario: " << nombre << std::endl;
    std::cout << "   📝 Problema: " << problem_title << std::endl;
    std::cout << "   🎚 Dificultad: " << difficulty << std::endl;
    std::cout << "   📄 Código (primeros 100 chars): "
              << codigo.substr(0, std::min(100, (int)codigo.length())) << "..." << std::endl;

    // Mostrar inputs/outputs si existen
    if (!input1.empty() && input1 != "NO_ENCONTRADO")
    {
        std::cout << "   📥 Input 1: " << input1 << std::endl;
        std::cout << "   📤 Output 1: " << output_esperado1 << std::endl;
    }
    if (!input2.empty() && input2 != "NO_ENCONTRADO")
    {
        std::cout << "   📥 Input 2: " << input2 << std::endl;
        std::cout << "   📤 Output 2: " << output_esperado2 << std::endl;
    }
    if (!input3.empty() && input3 != "NO_ENCONTRADO")
    {
        std::cout << "   📥 Input 3: " << input3 << std::endl;
        std::cout << "   📤 Output 3: " << output_esperado3 << std::endl;
    }
}

std::string Format::extractField(const std::string &json, const std::string &field)
{
    std::string pattern = "\"" + field + "\":\"";
    size_t start = json.find(pattern);
    if (start == std::string::npos)
    {
        pattern = "\"" + field + "\": \"";
        start = json.find(pattern);
        if (start == std::string::npos)
            return "NO_ENCONTRADO";
    }
    start += pattern.length();
    size_t end = json.find("\"", start);
    if (end == std::string::npos)
        return "ERROR";
    return json.substr(start, end - start);
}