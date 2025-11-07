#!/bin/bash
echo "🔨 Compilando servidor C++..."

# Crear carpeta de build si no existe
mkdir -p build
cd build

# Configurar con CMake
cmake -G "MSYS Makefiles" ..

# Compilar
make

echo "✅ Compilación completada!"
echo "🚀 Ejecutar con: ./CodeCoachServer.exe"