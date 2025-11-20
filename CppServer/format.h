// format.h
#ifndef FORMAT_H
#define FORMAT_H

#include <string>
#include <vector>
#include "json.hpp"

using json = nlohmann::json;

class Format
{
private:
    std::string nombre;
    std::string codigo;
    std::string problem_title;
    std::string difficulty;
    std::string function_name;
    std::string input1;
    std::string input2;
    std::string input3;
    std::string output_esperado1;
    std::string output_esperado2;
    std::string output_esperado3;

public:
    Format(const std::string &json_str);
    Format(const json &json_obj);

    std::string getNombre() const;
    std::string getCodigo() const;
    std::string getProblemTitle() const;
    std::string getFunctionName() const;
    std::string getDifficulty() const;
    
    // Inputs
    std::string getInput1() const;
    std::string getInput2() const;
    std::string getInput3() const;
    
    // Outputs
    std::string getOutputEsperado1() const;
    std::string getOutputEsperado2() const;
    std::string getOutputEsperado3() const;

    void mostrarInformacion() const;
    std::string getCodigoParaCompilar() const;
    std::vector<std::string> getInputs() const;
    std::vector<std::string> getOutputsEsperados() const;
    bool esValido() const;

private:
    std::string extraerCampo(const json &j, const std::string &campo);
    void inicializarDesdeJson(const json &j);
};

#endif