# Comparativa Técnica: MediaPipe Hand Landmarker (Python vs. C++)

Este documento detalla las diferencias arquitectónicas, de rendimiento y de implementación entre la versión original en Python y la recreación en C++.

## 1. Resumen de Rendimiento (Estimado)

| Métrica | Python (API Tasks) | C++ (Native Bazel) | Ganancia/Impacto |
| :--- | :--- | :--- | :--- |
| **Latencia de Inferencia** | ~35-45ms | ~20-28ms | C++ es ~40% más rápido |
| **Uso de Memoria (RAM)** | ~450 MB | ~180 MB | C++ consume <50% de RAM |
| **Carga de CPU (Single Thread)** | Alta (debido al GIL) | Eficiente (Multihilo nativo) | C++ escala mejor en multinúcleo |
| **Startup Time** | ~2.5 segundos | ~0.8 segundos | C++ inicia casi instantáneamente |

---

## 2. Diferencias Arquitectónicas

### Gestión de Memoria
- **Python:** Utiliza conteo de referencias y Garbage Collector. El paso de frames de OpenCV (NumPy) a MediaPipe (`mp.Image`) implica una abstracción de alto nivel que a veces requiere copias internas de memoria.
- **C++:** Utiliza punteros inteligentes (`std::unique_ptr`, `std::shared_ptr`). El paso de frames se realiza mediante `ImageFrame` que permite mapear directamente el buffer de memoria de OpenCV (`cv::Mat`) sin copias innecesarias, reduciendo la presión sobre el bus de datos.

### Concurrencia y Paralelismo
- **Python:** Limitado por el **Global Interpreter Lock (GIL)**. Aunque MediaPipe corre sus grafos en hilos nativos, la captura de cámara y el post-procesamiento en Python bloquean el intérprete, impidiendo un verdadero paralelismo en el código de usuario.
- **C++:** Soporta multihilo real. Es posible procesar la inferencia en un hilo, la captura en otro y la renderización en un tercero sin bloqueos mutuos, permitiendo tasas de FPS mucho más estables ( jitter reducido).

---

## 3. Stack Tecnológico

| Componente | Versión Python | Versión C++ |
| :--- | :--- | :--- |
| **Motor de Inferencia** | TFLite (vía Python Wrapper) | TFLite (C++ API Nativa) |
| **Procesamiento de Imagen** | OpenCV-Python (NumPy) | OpenCV C++ (Mat nativo) |
| **Orquestación** | MediaPipe Tasks Python | MediaPipe Framework / Bazel |
| **Compilación** | Interpretado (Bytecode) | Compilado (AOT - Ahead of Time) |

---

## 4. Análisis de Implementación (Dificultad vs. Control)

### Python (Facilidad)
- **Pro:** Desarrollo extremadamente rápido. Ideal para prototipado y experimentación.
- **Contra:** Difícil de distribuir como binario único. Dependencia de un entorno virtual (`venv`) pesado.

### C++ (Control Total)
- **Pro:** Permite optimizaciones a nivel de instrucciones (SIMD, AVX). El binario resultante es independiente y puede integrarse en sistemas embebidos o aplicaciones industriales con mínima sobrecarga.
- **Contra:** Curva de aprendizaje alta. El sistema de construcción (Bazel) es complejo y requiere descargar gigabytes de dependencias para la primera compilación.

---

## 5. Cuándo usar cada uno

### Elige Python si:
- Estás en fase de investigación o aprendizaje.
- El rendimiento de 25-30 FPS es suficiente para tu caso de uso.
- Necesitas integrar rápidamente librerías de IA/Data Science (Pandas, Scikit-learn).

### Elige C++ si:
- Estás desarrollando un producto final o comercial.
- Necesitas procesar múltiples cámaras simultáneamente.
- Vas a desplegar en hardware limitado (Raspberry Pi, Jetson Nano, Sistemas embebidos).
- El sistema requiere una latencia crítica (ej. control de prótesis o interfaces hápticas).

---

## 6. Observaciones sobre Fedora
En Fedora, la versión de C++ aprovecha mejor las librerías de sistema actualizadas. Sin embargo, debido a que Fedora es "rolling-edge" (versiones de software muy nuevas), Bazel puede requerir ajustes manuales para encontrar compiladores como GCC 14/15 o versiones de Python 3.14+, mientras que la versión de Python suele ser más tolerante a estos cambios.
