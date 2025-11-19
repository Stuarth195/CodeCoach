// format.cpp
#include "format.h"
#include <iostream>
#include <vector>

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
        // Inicializar con valores por defecto
        nombre = "ERROR_PARSE";
        codigo = "";
        problem_title = "";
        difficulty = "";
        input1 = input2 = input3 = "";
        output_esperado1 = output_esperado2 = output_esperado3 = "";
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
    difficulty = extraerCampo(j, "difficulty");
    input1 = extraerCampo(j, "input1");
    input2 = extraerCampo(j, "input2");
    input3 = extraerCampo(j, "input3");
    output_esperado1 = extraerCampo(j, "output_esperado1");
    output_esperado2 = extraerCampo(j, "output_esperado2");
    output_esperado3 = extraerCampo(j, "output_esperado3");
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

std::string Format::getCodigoParaCompilar() const
{
    return codigo;
}

std::vector<std::string> Format::getInputs() const
{
    std::vector<std::string> inputs;
    if (!input1.empty() && input1 != "NO_ENCONTRADO")
        inputs.push_back(input1);
    if (!input2.empty() && input2 != "NO_ENCONTRADO")
        inputs.push_back(input2);
    if (!input3.empty() && input3 != "NO_ENCONTRADO")
        inputs.push_back(input3);
    return inputs;
}

std::vector<std::string> Format::getOutputsEsperados() const
{
    std::vector<std::string> outputs;
    if (!output_esperado1.empty() && output_esperado1 != "NO_ENCONTRADO")
        outputs.push_back(output_esperado1);
    if (!output_esperado2.empty() && output_esperado2 != "NO_ENCONTRADO")
        outputs.push_back(output_esperado2);
    if (!output_esperado3.empty() && output_esperado3 != "NO_ENCONTRADO")
        outputs.push_back(output_esperado3);
    return outputs;
}

bool Format::esValido() const
{
    return !nombre.empty() && nombre != "NO_ENCONTRADO" &&
           !codigo.empty() && codigo != "NO_ENCONTRADO" &&
           !problem_title.empty() && problem_title != "NO_ENCONTRADO";
}

void Format::mostrarInformacion() const
{
    std::cout << "🔍 INFORMACIÓN DEL FORMULARIO:" << std::endl;
    std::cout << "   👤 Usuario: " << nombre << std::endl;
    std::cout << "   📝 Problema: " << problem_title << std::endl;
    std::cout << "   🎚 Dificultad: " << difficulty << std::endl;
    std::cout << "   📄 Código (primeros 100 chars): "
              << codigo.substr(0, std::min(100, (int)codigo.length())) << "..." << std::endl;

    // Mostrar inputs/outputs si existen
    auto inputs = getInputs();
    auto outputs = getOutputsEsperados();

    for (size_t i = 0; i < inputs.size(); ++i)
    {
        std::cout << "   📥 Input " << (i + 1) << ": " << inputs[i] << std::endl;
        if (i < outputs.size())
        {
            std::cout << "   📤 Output " << (i + 1) << ": " << outputs[i] << std::endl;
        }
    }

    std::cout << "   ✅ Formato válido: " << (esValido() ? "Sí" : "No") << std::endl;
}

std::string Format::extraerCampo(const json &j, const std::string &campo)
{
    try
    {
        if (j.contains(campo) && !j[campo].is_null())
        {
            if (j[campo].is_string())
            {
                return j[campo].get<std::string>();
            }
            else
            {
                // Si no es string, convertirlo a string
                return j[campo].dump();
            }
        }
    }
    catch (const json::exception &e)
    {
        std::cerr << "⚠️ Error extrayendo campo '" << campo << "': " << e.what() << std::endl;
    }
    return "NO_ENCONTRADO";
}