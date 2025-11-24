<div align="center">

<h1 align="center">💻 CodeCoach — Plataforma de Retos de Programación</h1>

<p align="center">
  <img alt="Lenguaje principal" src="https://img.shields.io/badge/C++-Backend-blue.svg?style=for-the-badge&logo=cplusplus&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-GUI-yellow.svg?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Base de Datos" src="https://img.shields.io/badge/MongoDB-Database-green.svg?style=for-the-badge&logo=mongodb&logoColor=white">
  <img alt="Framework GUI" src="https://img.shields.io/badge/Qt-Interface-brightgreen.svg?style=for-the-badge&logo=qt&logoColor=white">
  <img alt="Estado" src="https://img.shields.io/badge/Estado-En%20Desarrollo-orange.svg?style=for-the-badge">
</p>

<p align="center">
  🚀 <b>Plataforma de entrenamiento para entrevistas técnicas de programación</b> 🚀
</p>

</div>

---

## 📘 Descripción General

**CodeCoach** es una plataforma diseñada para que los estudiantes practiquen ejercicios de programación estilo _LeetCode_ o _HackerRank_, con un enfoque educativo.

El sistema permite:

1. **Registrarse e iniciar sesión** con autenticación segura
2. **Seleccionar problemas** desde una base de datos MongoDB
3. **Escribir y enviar código C++** desde un editor integrado
4. **Recibir evaluación automática** en tiempo real
5. **Ver estadísticas de progreso y ranking**
6. **Obtener retroalimentación detallada** de cada solución

---

## 🏗️ Arquitectura Implementada

| Módulo                    | Tecnología        | Estado          | Descripción                     |
| ------------------------- | ----------------- | --------------- | ------------------------------- |
| **Interfaz GUI**          | Python + PyQt5    | ✅ Implementado | Interfaz moderna con navegación |
| **Servidor HTTP C++**     | C++17 + Sockets   | ✅ Implementado | Endpoints REST personalizados   |
| **Motor de Compilación**  | C++ + MinGW       | ✅ Implementado | Compilación y ejecución segura  |
| **Base de Datos**         | MongoDB + pymongo | ✅ Implementado | Users, problems, stats          |
| **Autenticación**         | Python + SHA256   | ✅ Implementado | Validación de credenciales      |
| **Sistema de Evaluación** | C++ + JSON        | ✅ Implementado | Test cases múltiples            |

---

## 🔄 Flujo de Datos

```

GUI Python (PyQt5)
↓ (HTTP JSON)
Servidor C++ (localhost:5000)
↓ (Compilación y ejecución)
Motor de Evaluación
↓ (Resultados JSON)
GUI Python + MongoDB
↓
Base de Datos + Ranking

```

---

## ⚙️ Tecnologías Utilizadas

### 🔧 Backend C++

- Servidor HTTP con sockets
- Compilación con **MinGW g++**
- Manejo de JSON con `nlohmann/json`
- Sandbox básico con procesos Windows

### 🎨 Frontend Python

- Interfaz con PyQt5 (tema oscuro)
- Cliente HTTP con `requests`
- Base de datos con `pymongo`
- Autenticación con SHA256

### 🗄️ Base de Datos MongoDB

- Colecciones: `users`, `problems`, `user_stats`
- Documentos basados en JSON

---

## 🚀 Ejecución del Proyecto

### 🔧 Prerrequisitos

- **MSYS2 MINGW64**
- **Python 3.8+**
- **MongoDB local**
- **MinGW g++**

### 📦 Instalación en MSYS2

```bash
pacman -Syu
pacman -S --needed base-devel mingw-w64-x86_64-toolchain
pacman -S mingw-w64-x86_64-curl mingw-w64-x86_64-cmake
```

### ▶️ Ejecutar servidor C++

```bash
cd CppServer
g++ -o server main.cpp RequestHandler.cpp format.cpp runner.cpp -lcurl -lws2_32 -std=c++17
./server.exe
```

### ▶️ Ejecutar GUI Python

```bash
cd /ruta/al/proyecto
python Gui.py
```

### ⚡ Script de compilación rápida

```bash
./compile.sh
```

### ✔️ Verificar instalación

```bash
g++ --version
python --version
mongod --version
```

---

## 📊 Características

### ✔️ Completadas

- Sistema de usuarios y autenticación
- Base de datos de problemas real
- Editor de código C++ con resaltado
- Compilación remota desde GUI
- Evaluación automática con múltiples test cases
- Sistema de puntuación y ranking
- UI moderna y responsiva
- Manejo robusto de errores

### 🔄 En Desarrollo

- Sandbox con Docker
- IA para retroalimentación
- Métricas de ejecución (tiempo/memoria)
- Soporte para más lenguajes

---

## 📂 Estructura de Datos

### 📝 Ejemplo de problema (MongoDB)

```json
{
  "title": "numero_palindromo",
  "category": "Matemáticas",
  "difficulty": "Fácil",
  "statement": "Dado un entero x, devuelve 'true' si x es un palíndromo...",
  "examples": [
    {
      "input_raw": "121",
      "output_raw": "true",
      "explanation": "121 se lee igual en ambos sentidos"
    }
  ]
}
```

### 🧪 Ejemplo de resultados de evaluación

```json
{
  "status": "success",
  "passed_count": 3,
  "total_tests": 3,
  "score": 30,
  "problem_solved": true,
  "tests": [
    {
      "test_id": 1,
      "input": "121",
      "obtained": "true",
      "passed": true
    }
  ]
}
```

---

## 🗂️ Estructura del Proyecto

```
CodeCoach/
├── CppServer/
│   ├── main.cpp
│   ├── RequestHandler.cpp
│   ├── runner.cpp
│   └── format.cpp
├── logic/
│   ├── auth_logic.py
│   ├── database_handler.py
│   └── user_models.py
├── Gui.py
├── LoginWindow.py
├── AuxCreator.py
└── PyLogic.py
```

---

## 🛡️ Seguridad y Sandbox

| Característica              | Implementación          | Estado           |
| --------------------------- | ----------------------- | ---------------- |
| Ejecución aislada           | Procesos independientes | ✅               |
| Timeout por ejecución       | 2s                      | ✅               |
| Validación básica de código | Pre-análisis            | ✅               |
| Sandbox Docker              | Contenedor aislado      | 🔄 En desarrollo |

---

## 📈 Próximos Pasos

1. Integrar Docker para sandbox seguro
2. IA Coach con retroalimentación inteligente
3. Métricas avanzadas de rendimiento
4. Soporte para más lenguajes
5. Suite completa de tests unitarios
6. Deployment en la nube

---

<div align="center">

### 👨‍💻 Desarrollado por

**Raúl Stuarth Ramírez Villegas**
**David Cordero Zuñiga**
**Gok Cheng Liang**
— CE2103 | Instituto Tecnológico de Costa Rica

> _"El mejor código no solo resuelve problemas, enseña cómo pensar."_

**📌 Servidor ejecutándose en:** `http://localhost:5000`

</div>
```

---


Aquí tienes un **README completamente ordenado**, limpio y listo para **copiar y pegar** en tu proyecto **LeetAI**.
Incluye **los JSON de los problemas** + **las soluciones en C++**, todo perfectamente organizado.
No uso bloques especiales fuera del markdown normal (para que GitHub lo lea bien).

---

# 🚀 LeetAI — Banco de Problemas + Soluciones en C++

Este repositorio contiene una colección de problemas estilo LeetCode diseñados para **LeetAI**, junto con su **estructura JSON lista para MongoDB** y su **implementación en C++**.

Cada problema incluye:

* Estructura JSON (para BD)
* Descripción del enunciado
* Ejemplos
* Solución en C++

---

# 📘 **Índice de Problemas**

| #  | Nombre             | Categoría           | Dificultad |
| -- | ------------------ | ------------------- | ---------- |
| 1  | es_numero_par      | Matemáticas Básicas | Fácil      |
| 2  | suma_digitos       | Matemáticas         | Fácil      |
| 3  | invertir_palabra   | Strings             | Fácil      |
| 4  | calcular_promedio  | Matemáticas         | Fácil      |
| 5  | es_vocal           | Caracteres          | Fácil      |
| 6  | encontrar_maximo   | Arrays              | Fácil      |
| 7  | fibonacci          | Matemáticas         | Medio      |
| 8  | contar_palabras    | Strings             | Medio      |
| 9  | es_palindromo      | Strings             | Medio      |
| 10 | matriz_transpuesta | Matrices            | Difícil    |

---

# 📂 **Problemas + Soluciones**

---

## 1. **Es Número Par**

### JSON

```json
{
  "title": "es_numero_par",
  "category": "Matemáticas Básicas",
  "difficulty": "Fácil",
  "statement": "Dado un número entero n, determina si es par. Retorna 1 si es par, 0 si es impar.",
  "big_o_expected": "O(1)",
  "function_type": "bool",
  "function_name": "es_numero_par",
  "examples": [
    { "input_raw": "4", "input_pretty": "Input: n = 4", "output_raw": "1", "output_pretty": "Output: true" },
    { "input_raw": "7", "input_pretty": "Input: n = 7", "output_raw": "0", "output_pretty": "Output: false" },
    { "input_raw": "0", "input_pretty": "Input: n = 0", "output_raw": "1", "output_pretty": "Output: true" }
  ]
}
```

### Solución C++

```cpp
bool es_numero_par(int n) {
    return n % 2 == 0;
}
```

---

## 2. **Suma Dígitos**

### JSON

```json
{
  "title": "suma_digitos",
  "category": "Matemáticas",
  "difficulty": "Fácil",
  "statement": "Dado un número entero n, retorna la suma de sus dígitos.",
  "big_o_expected": "O(d) donde d es el número de dígitos",
  "function_type": "int",
  "function_name": "suma_digitos",
  "examples": [
    { "input_raw": "123", "input_pretty": "Input: n = 123", "output_raw": "6", "output_pretty": "Output: 6" },
    { "input_raw": "987", "input_pretty": "Input: n = 987", "output_raw": "24", "output_pretty": "Output: 24" },
    { "input_raw": "0", "input_pretty": "Input: n = 0", "output_raw": "0", "output_pretty": "Output: 0" }
  ]
}
```

### Solución C++

```cpp
int suma_digitos(int n) {
    int suma = 0;
    n = abs(n);
    while (n > 0) {
        suma += n % 10;
        n /= 10;
    }
    return suma;
}
```

---

## 3. **Invertir Palabra**

### JSON

```json
{
  "title": "invertir_palabra",
  "category": "Strings",
  "difficulty": "Fácil",
  "statement": "Dada una cadena s, retorna la cadena invertida.",
  "big_o_expected": "O(n)",
  "function_type": "string",
  "function_name": "invertir_palabra",
  "examples": [
    { "input_raw": "hola", "input_pretty": "Input: s = \"hola\"", "output_raw": "aloh", "output_pretty": "Output: \"aloh\"" },
    { "input_raw": "mundo", "input_pretty": "Input: s = \"mundo\"", "output_raw": "odnum", "output_pretty": "Output: \"odnum\"" },
    { "input_raw": "a", "input_pretty": "Input: s = \"a\"", "output_raw": "a", "output_pretty": "Output: \"a\"" }
  ]
}
```

### Solución C++

```cpp
string invertir_palabra(string s) {
    reverse(s.begin(), s.end());
    return s;
}
```

---

## 4. **Calcular Promedio**

### JSON

```json
{
  "title": "calcular_promedio",
  "category": "Matemáticas",
  "difficulty": "Fácil",
  "statement": "Dado un arreglo de números, calcula el promedio.",
  "big_o_expected": "O(n)",
  "function_type": "double",
  "function_name": "calcular_promedio",
  "examples": [
    { "input_raw": "[1,2,3,4,5]", "output_raw": "3.0" },
    { "input_raw": "[10,20,30]", "output_raw": "20.0" },
    { "input_raw": "[0]", "output_raw": "0.0" }
  ]
}
```

### Solución C++

```cpp
double calcular_promedio(vector<int> nums) {
    if (nums.empty()) return 0.0;
    double suma = 0;
    for (int n : nums) suma += n;
    return suma / nums.size();
}
```

---

## 5. **Es Vocal**

### JSON

```json
{
  "title": "es_vocal",
  "category": "Caracteres",
  "difficulty": "Fácil",
  "statement": "Dado un carácter c, determina si es una vocal.",
  "big_o_expected": "O(1)",
  "function_type": "bool",
  "function_name": "es_vocal",
  "examples": [
    { "input_raw": "a", "output_raw": "1" },
    { "input_raw": "E", "output_raw": "1" },
    { "input_raw": "z", "output_raw": "0" }
  ]
}
```

### Solución C++

```cpp
bool es_vocal(char c) {
    c = tolower(c);
    return c=='a' || c=='e' || c=='i' || c=='o' || c=='u';
}
```

---

## 6. **Encontrar Máximo**

### JSON

```json
{
  "title": "encontrar_maximo",
  "category": "Arrays",
  "difficulty": "Fácil",
  "statement": "Dado un arreglo, retorna el valor máximo.",
  "big_o_expected": "O(n)",
  "function_type": "int",
  "function_name": "encontrar_maximo",
  "examples": [
    { "input_raw": "[1,5,3,9,2]", "output_raw": "9" },
    { "input_raw": "[-1,-5,-3]", "output_raw": "-1" },
    { "input_raw": "[42]", "output_raw": "42" }
  ]
}
```

### Solución C++

```cpp
int encontrar_maximo(vector<int> nums) {
    if (nums.empty()) return INT_MIN;
    int maximo = nums[0];
    for (int n : nums)
        if (n > maximo) maximo = n;
    return maximo;
}
```

---

## 7. **Fibonacci**

### JSON

```json
{
  "title": "fibonacci",
  "category": "Matemáticas",
  "difficulty": "Medio",
  "statement": "Retorna el n-ésimo número Fibonacci.",
  "big_o_expected": "O(n)",
  "function_type": "int",
  "function_name": "fibonacci",
  "examples": [
    { "input_raw": "0", "output_raw": "0" },
    { "input_raw": "1", "output_raw": "1" },
    { "input_raw": "6", "output_raw": "8" }
  ]
}
```

### Solución C++

```cpp
int fibonacci(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        int t = a + b;
        a = b;
        b = t;
    }
    return b;
}
```

---

## 8. **Contar Palabras**

### JSON

```json
{
  "title": "contar_palabras",
  "category": "Strings",
  "difficulty": "Medio",
  "statement": "Cuenta las palabras separadas por espacios.",
  "big_o_expected": "O(n)",
  "function_type": "int",
  "function_name": "contar_palabras",
  "examples": [
    { "input_raw": "Hola mundo", "output_raw": "2" },
    { "input_raw": "   espacios   multiples   ", "output_raw": "2" },
    { "input_raw": "", "output_raw": "0" }
  ]
}
```

### Solución C++

```cpp
int contar_palabras(string s) {
    int contador = 0;
    bool en_palabra = false;
    for (char c : s) {
        if (c != ' ' && !en_palabra) {
            contador++;
            en_palabra = true;
        } else if (c == ' ') {
            en_palabra = false;
        }
    }
    return contador;
}
```

---

## 9. **Es Palíndromo**

### JSON

```json
{
  "title": "es_palindromo",
  "category": "Strings",
  "difficulty": "Medio",
  "statement": "Determina si una cadena es palíndromo ignorando símbolos y mayúsculas.",
  "big_o_expected": "O(n)",
  "function_type": "bool",
  "function_name": "es_palindromo",
  "examples": [
    { "input_raw": "Anita lava la tina", "output_raw": "1" },
    { "input_raw": "A man, a plan, a canal: Panama", "output_raw": "1" },
    { "input_raw": "hello world", "output_raw": "0" }
  ]
}
```

### Solución C++

```cpp
bool es_palindromo(string s) {
    int i = 0, j = s.length() - 1;
    while (i < j) {
        while (i < j && !isalnum(s[i])) i++;
        while (i < j && !isalnum(s[j])) j--;
        if (tolower(s[i]) != tolower(s[j])) return false;
        i++; j--;
    }
    return true;
}
```

---

## 10. **invertir lista enlazada**

### JSON

```json
}
  "title": "invertir_lista_enlazada",
  "category": "Listas Enlazadas",
  "difficulty": "Medio",
  "statement": "Dada la cabeza 'head' de una lista enlazada simple, invierte la lista y devuelve la cabeza de la lista invertida.",
  "big_o_expected": "O(n)",
  "function_type": "array",
  "function_name": "invertir_lista_enlazada",
  "examples": [
    {
      "input_raw": "[1, 2, 3, 4, 5]",
      "input_pretty": "Input: head = [1, 2, 3, 4, 5]",
      "output_raw": "[5, 4, 3, 2, 1]",
      "output_pretty": "Output: [5, 4, 3, 2, 1]"
    },
    {
      "input_raw": "[1, 2]",
      "input_pretty": "Input: head = [1, 2]",
      "output_raw": "[2, 1]",
      "output_pretty": "Output: [2, 1]"
    },
    {
      "input_raw": "[]",
      "input_pretty": "Input: head = []",
      "output_raw": "[]",
      "output_pretty": "Output: []"
    }
  ]
}
```

### Solución C++

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

vector<int> invertir_lista_enlazada(vector<int> head) {
    // Caso especial: lista vacía
    if (head.empty()) {
        return {};
    }
    
    // Crear una copia y usar reverse de algorithm
    vector<int> resultado = head;
    reverse(resultado.begin(), resultado.end());
    return resultado;
}
```

---


