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
    std::string input1;
    std::string input2;
    std::string input3;
    std::string output_esperado1;
    std::string output_esperado2;
    std::string output_esperado3;

public:
    // Constructor que parsea el JSON usando nlohmann
    Format(const std::string &json_str);

    // Constructor alternativo que recibe objeto json directamente
    Format(const json &json_obj);

    // Getters para todos los atributos
    std::string getNombre() const;
    std::string getCodigo() const;
    std::string getProblemTitle() const;
    std::string getDifficulty() const;
    std::string getInput1() const;
    std::string getInput2() const;
    std::string getInput3() const;
    std::string getOutputEsperado1() const;
    std::string getOutputEsperado2() const;
    std::string getOutputEsperado3() const;

    // Método para mostrar información
    void mostrarInformacion() const;

    // Método para obtener el código (útil para compilación)
    std::string getCodigoParaCompilar() const;

    // Método para obtener todos los inputs como vector
    std::vector<std::string> getInputs() const;

    // Método para obtener todos los outputs esperados como vector
    std::vector<std::string> getOutputsEsperados() const;

    // Método para validar que el JSON tiene la estructura correcta
    bool esValido() const;

private:
    // Método auxiliar para extraer campos del JSON de forma segura
    std::string extraerCampo(const json &j, const std::string &campo);

    // Método para inicializar desde objeto json
    void inicializarDesdeJson(const json &j);
};

#endif