<div align="center">

<h1 align="center">💻 CodeCoach — Plataforma de Retos de Programación</h1>

<p align="center">
  <img alt="Lenguaje principal" src="https://img.shields.io/badge/C++-Backend-blue.svg?style=for-the-badge&logo=cplusplus&logoColor=white">
  <img alt="IA" src="https://img.shields.io/badge/Python-IA_Coach-yellow.svg?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Base de datos" src="https://img.shields.io/badge/MongoDB-Database-green.svg?style=for-the-badge&logo=mongodb&logoColor=white">
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
El sistema permite al usuario:

1. Seleccionar un problema.
2. Escribir y enviar su código en C++.
3. Recibir una evaluación automática y retroalimentación de una IA entrenadora.

---

## 🧩 Arquitectura General

| Módulo                 | Lenguaje / Tecnología | Descripción                                                                 |
| ---------------------- | -------------------- | --------------------------------------------------------------------------- |
| **Interfaz (GUI)**     | Qt (C++) ✅          | Permite listar problemas, editar código, ver resultados y feedback de IA.   |
| **Gestor de Problemas**| C++ + MongoDB 🔖     | Administra problemas, test cases y metadatos almacenados en base de datos.  |
| **Motor de Evaluación**| C++ ✅               | Compila y ejecuta código de usuario en un entorno aislado (*sandbox*).      |
| **Analizador IA**      | Python + GPT-J 🔖    | Recibe código, errores y resultados; genera feedback inteligente.           |
| **Base de Datos**      | MongoDB 🔖           | Guarda usuarios, problemas, envíos y resultados.                            |

---

## 🔗 Comunicación entre Componentes

| Canal / Protocolo | Estado | Descripción |
| ------------------ | ------- | ------------ |
| REST API (C++)     | 🔖 Pendiente | Comunicación entre GUI, motor y gestor. Framework por investigar (Crow, Drogon, Pistache). |
| JSON               | 🔖 Pendiente | Formato estándar de datos entre módulos. Librería a definir (nlohmann/json o RapidJSON). |
| Conexión MongoDB   | 🔖 Pendiente | Evaluar uso de `mongocxx` o REST intermedio para comunicación. |

---

## ⚙️ Ejecución y Seguridad

| Elemento                 | Estado      | Detalle                                                                 |
| ------------------------- | ----------- | ----------------------------------------------------------------------- |
| **Sandbox**               | ✅ Definido | El código se ejecutará en un entorno aislado para seguridad.            |
| **Medición de tiempo**    | 🔖 Pendiente | Inicialmente se usará medición por Ticks; sujeta a mejora.              |
| **Medición de memoria**   | ✅ Fijo      | MB como unidad estándar para reportes.                                 |

---

## 🧠 Inteligencia Artificial

| Elemento                  | Estado       | Detalle                                                                 |
| -------------------------- | ------------ | ----------------------------------------------------------------------- |
| **Modelo base (GPT-J)**    | ✅ Propuesto  | Modelo open-source ejecutado en Python.                                |
| **API de IA**              | 🔖 Pendiente  | Evaluando opciones (GPT-J local, HuggingFace, Mistral).                |
| **Datos enviados al modelo** | ✅ Definido   | Código fuente, errores de compilación y resultados de test.            |
| **Formato de feedback**    | 🔖 Pendiente  | Por definir esquema JSON de respuesta adaptada.                        |

---

## 🧱 Modelado y Diseño

| Componente | Estado | Descripción |
| ----------- | ------- | ------------ |
| **Clases principales** | 🔖 Parcial | `Usuario`, `Problema` definidas; faltan `Evaluador`, `Analizador`, `Feedback`. |
| **Patrones sugeridos** | ✅ Definido | `MVC` para GUI y `Command` para ejecución de código. |
| **Diagrama UML** | 🔖 Pendiente | Se generará al finalizar diseño de clases base. |

---

## 🧪 Tecnologías y Herramientas Evaluadas

| Categoría | Opción Recomendada | Pros | Contras |
| ---------- | ------------------ | ---- | -------- |
| **Framework REST (C++)** | **Drogon** | Moderno, rápido, soporte WebSocket. | Curva de aprendizaje moderada. |
| **JSON** | **nlohmann/json** | Simple y moderno. | Lento con grandes volúmenes. |
| **MongoDB Driver** | **mongocxx** | Oficial, documentado. | Compilación compleja. |
| **Sandbox** | **Docker / isolate** | Alta seguridad, estándar en jueces online. | Sobrecarga de recursos. |
| **Modelo LLM** | **CodeLlama / GPT-J** | Open-source, buen equilibrio. | Requiere GPU o API. |

---

## 🗂️ Estructura Inicial del Repositorio

```bash
CodeCoach/
├── gui/                # Interfaz en Qt
├── core/               # Motor de evaluación
├── ai_coach/           # Lógica IA en Python
├── db/                 # Conexión y modelos MongoDB
├── tests/              # Casos de prueba y validación
├── docs/               # Diagramas y documentación
└── README.md

## 🚧 Estado Actual

| Etapa                        | Progreso     |
| ---------------------------- | ------------ |
| Modelado general del sistema | ✅            |
| Diseño de GUI base en Qt     | ✅            |
| Definición de API y drivers  | 🔖 Pendiente |
| Motor de ejecución (sandbox) | ✅            |
| Integración con IA           | 🔖 Pendiente |
| Esquema MongoDB              | 🔖 Pendiente |
| Documentación UML            | 🔖 Pendiente |

---

## 📅 Organización del Proyecto

* Desarrollo en **sprints** de 2 semanas.
* Asignación **equitativa** de historias por puntos.
* Gestión de ramas en **GitHub** por módulo (`gui/`, `core/`, `ai/`, etc.).
* Integración continua planificada tras la primera versión funcional.

---

<div align="center">

### 👨‍💻 Desarrollado por

**Raúl Stuarth Ramírez Villegas** — CE2103 | Instituto Tecnológico de Costa Rica

> *“El mejor código no solo resuelve problemas, enseña cómo pensar.”*

</div>
```

---

