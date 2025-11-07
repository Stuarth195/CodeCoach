FROM ubuntu:22.04

# Evitar prompts durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gdb \
    git \
    curl \
    wget \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias C++ (simulamos MSVC con g++)
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de construcción
COPY CMakeLists.txt .
COPY include/ include/
COPY src/ src/

# Crear directorio de construcción y compilar
RUN mkdir build && cd build && \
    cmake .. && \
    make -j4

# Exponer puerto
EXPOSE 5000

# Comando para ejecutar el servidor
CMD ["./build/CodeCoachServer"]