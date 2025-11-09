// format.h
#ifndef FORMAT_H
#define FORMAT_H

#include <string>

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
    // Constructor que parsea el JSON// format.h
#ifndef FORMAT_H
#define FORMAT_H

#include <string>

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
        // Constructor que parsea el JSON
        Format(const std::string &json);

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

        // Método para mostrar información (opcional)
        void mostrarInformacion() const;

    private:
        // Método auxiliar para extraer campos del JSON
        std::string extractField(const std::string &json, const std::string &field);
    };

#endif
    Format(const std::string &json);

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

    // Método para mostrar información (opcional)
    void mostrarInformacion() const;

private:
    // Método auxiliar para extraer campos del JSON
    std::string extractField(const std::string &json, const std::string &field);
};

#endif