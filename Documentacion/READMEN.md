# 🚀 CodeCoach - Servidor C++

## 📦 Comandos de Instalación (MSYS2)

### Actualizar e Instalar Dependencias

```bash
# Actualizar paquetes
pacman -Syu

# Instalar herramientas de desarrollo
pacman -S --needed base-devel mingw-w64-x86_64-toolchain

# Instalar cURL y CMake
pacman -S mingw-w64-x86_64-curl mingw-w64-x86_64-cmake
```

## 🖥️ Ejecutar Servidor C++

### Método Rápido (Compilación Directa)

```bash
cd /c/Users/shoko/OneDrive/Documents/progra/Repositorilos_GitHub/CodeCoach/CppServer
 g++ -o server main.cpp RequestHandler.cpp format.cpp runner.cpp -lcurl -lws2_32 -std=c++17

./server.exe
```

### Método con CMake solo en ultia instancia

```bash
cd /c/Users/shoko/OneDrive/Documents/progra/Repositorilos_GitHub/CodeCoach/CppServer

# Limpiar y recompilar
rm -rf build
mkdir build
cd build
cmake -G "MinGW Makefiles" ..
make
./CodeCoachServer.exe
```

### Usar Script de Compilación

```bash
cd /c/Users/shoko/OneDrive/Documents/progra/Repositorilos_GitHub/CodeCoach/CppServer
./compile.sh
```

### Verificar instalación:

```bash
g++ --version
curl --version
cmake --version
```

## 📝 Notas Importantes

- **Siempre usar MSYS2 MINGW64** (terminal Azul)
- **Ejecutar servidor primero**, luego las pruebas
- El servidor escucha en: `http://localhost:5000`

---

**¡Listo para recibir requests de la GUI!**
