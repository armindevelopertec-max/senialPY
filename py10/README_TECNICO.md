# Documentación Técnica: Sistema de Control por Gestos para Robot (ESP32)

Este script (`practica_controlManos.py`) implementa un sistema de control de visión artificial en tiempo real que permite operar un robot móvil (basado en ESP32) mediante gestos manuales. El sistema está optimizado para entornos Linux (Fedora) y utiliza comunicación Bluetooth de baja latencia.

## 1. Arquitectura del Sistema

El software se divide en cuatro capas principales:
1.  **Capa de Adquisición:** Captura de video mediante OpenCV.
2.  **Capa de Procesamiento:** Extracción de 21 puntos clave (landmarks) de la mano usando MediaPipe Hands.
3.  **Capa de Lógica (Filtro Robusto):** Clasificación de gestos mediante relaciones espaciales y filtrado por confirmación (Hysteresis).
4.  **Capa de Comunicación:** Envío de comandos persistentes vía Sockets Bluetooth (RFCOMM).

---

## 2. Lógica de Detección de Gestos

El sistema utiliza coordenadas normalizadas (X, Y) para identificar gestos específicos, priorizando la estabilidad y evitando falsos positivos.

### Mapa de Gestos

| Gesto Visual | Comando | Significado Técnico | Lógica de Detección |
| :--- | :--- | :--- | :--- |
| **Palma Abierta** | `S` | **STOP** | Detección de 3 o más dedos extendidos hacia arriba. |
| **Índice Izq** | `K:0,1.8` | **Giro Izquierda** | Eje X del índice < Eje X del nudillo (Delta > 0.06). |
| **Índice Der** | `K:0,-1.8` | **Giro Derecha** | Eje X del índice > Eje X del nudillo (Delta > 0.06). |
| **Pulgar Arriba** | `K:0.25,0` | **Avanzar** | Pulgar arriba + Índice cerrado (evita conflictos con giros). |
| **Pulgar Abajo** | `K:-0.20,0` | **Retroceder** | Pulgar abajo + Índice cerrado. |

### Prioridad de Comando
Para evitar comportamientos erráticos cuando se muestran múltiples dedos, el script aplica la siguiente jerarquía:
1.  **STOP:** Si se detecta palma abierta, se anula cualquier otro movimiento.
2.  **Giro:** Si el dedo índice está apuntando lateralmente, se prioriza el giro sobre el avance/retroceso.
3.  **Lineal:** Solo si no hay giros activos, se procesa la posición del pulgar.

---

## 3. Robustez y Filtrado (Noise Blocking)

Una de las mejoras críticas de esta versión es el sistema de **Confirmación por Fotogramas**:

-   **Variable `UMBRAL_CONFIRMACION`:** Configurada por defecto en `3`.
-   **Funcionamiento:** Un gesto no se envía al robot inmediatamente. Debe ser detectado durante 3 fotogramas consecutivos. Si aparece un dedo "fantasma" por un solo instante, los contadores se resetean, evitando que el robot pegue tirones innecesarios.
-   **Enfoque Único:** El sistema detecta múltiples manos pero **solo procesa la primera** (`multi_hand_landmarks[0]`), ignorando a personas o manos en el fondo.

---

## 4. Protocolo de Comunicación

### Persistencia de Comandos
A diferencia de sistemas estándar, este script utiliza **Envío Persistente**. El comando actual se envía al robot en cada iteración del loop (aprox. cada 10-20ms).
*   **Ventaja:** Si el ESP32 pierde un paquete por interferencia Bluetooth, recibirá el siguiente inmediatamente.
*   **Seguridad:** El robot solo se detiene si recibe explícitamente el comando `S` o si entra en marcha el Watchdog del firmware por pérdida total de conexión.

### Bluetooth en Fedora
Se ha eliminado la dependencia de `pybluez` en favor de `socket.AF_BLUETOOTH`. Esto permite una conexión directa con la pila de protocolos BlueZ de Linux sin necesidad de compilar librerías antiguas.

---

## 5. Requisitos e Instalación

### Dependencias (Python 3.10+)
```bash
pip install opencv-python mediapipe numpy
```

### Ejecución
**Modo Real (con Robot):**
```bash
python practica_controlManos.py --mac CC:7B:5C:23:4C:E2
```

**Modo Emulación (Pruebas de cámara):**
```bash
python practica_controlManos.py --mock
```

---

## 6. Parámetros Técnicos Ajustables

-   **Velocidad Lineal:** Modificar `K:0.25,0` (0.25 m/s).
-   **Velocidad de Giro:** Modificar `K:0,1.8` (1.8 rad/s).
-   **Sensibilidad:** Ajustar `min_detection_confidence` (0.7) para entornos con poca luz.
-   **Filtro de Ruido:** Subir `UMBRAL_CONFIRMACION` para mayor estabilidad a costa de una ligera latencia.


(venv) armintec@fedora:~/Arduino/senialPY/py10$ cat .python-version
3.10.20
(venv) armintec@fedora:~/Arduino/senialPY/py10$ cat requirements.txt
mediapipe==0.10.21
opencv-python==4.13.0.92
numpy==1.26.4
