cmake_minimum_required(VERSION 3.10)
project(CodeCoachRunner)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (WIN32)
    add_definitions(-DWIN32_LEAN_AND_MEAN)
endif()

# Añadir ruta include para nlohmann (espera CppServer/include/nlohmann/json.hpp)
include_directories(${CMAKE_SOURCE_DIR}/../include)

add_executable(runner runner.cpp)
# No librerías externas necesarias para prototipo