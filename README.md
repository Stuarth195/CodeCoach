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

**CodeCoach** es una plataforma diseñada para que los estudiantes practiquen ejercicios de programación estilo *LeetCode* o *HackerRank*, con un enfoque educativo.

El sistema permite:

1. **Registrarse e iniciar sesión** con autenticación segura  
2. **Seleccionar problemas** desde una base de datos MongoDB  
3. **Escribir y enviar código C++** desde un editor integrado  
4. **Recibir evaluación automática** en tiempo real  
5. **Ver estadísticas de progreso y ranking**  
6. **Obtener retroalimentación detallada** de cada solución  

---

## 🏗️ Arquitectura Implementada

| Módulo | Tecnología | Estado | Descripción |
|-------|------------|--------|-------------|
| **Interfaz GUI** | Python + PyQt5 | ✅ Implementado | Interfaz moderna con navegación |
| **Servidor HTTP C++** | C++17 + Sockets | ✅ Implementado | Endpoints REST personalizados |
| **Motor de Compilación** | C++ + MinGW | ✅ Implementado | Compilación y ejecución segura |
| **Base de Datos** | MongoDB + pymongo | ✅ Implementado | Users, problems, stats |
| **Autenticación** | Python + SHA256 | ✅ Implementado | Validación de credenciales |
| **Sistema de Evaluación** | C++ + JSON | ✅ Implementado | Test cases múltiples |

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

````

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
````

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

* Sistema de usuarios y autenticación
* Base de datos de problemas real
* Editor de código C++ con resaltado
* Compilación remota desde GUI
* Evaluación automática con múltiples test cases
* Sistema de puntuación y ranking
* UI moderna y responsiva
* Manejo robusto de errores

### 🔄 En Desarrollo

* Sandbox con Docker
* IA para retroalimentación
* Métricas de ejecución (tiempo/memoria)
* Soporte para más lenguajes

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
| Ejecución aislada           | Procesos independientes | ✅                |
| Timeout por ejecución       | 2s                      | ✅                |
| Validación básica de código | Pre-análisis            | ✅                |
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

> *"El mejor código no solo resuelve problemas, enseña cómo pensar."*

**📌 Servidor ejecutándose en:** `http://localhost:5000`

</div>
```

---


