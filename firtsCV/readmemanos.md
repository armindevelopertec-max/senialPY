# Detector de Manos con MediaPipe Tasks API

Este proyecto implementa un detector de manos en tiempo real utilizando la API moderna de MediaPipe (**Tasks API**). Se ha migrado desde la API legada `mediapipe.solutions` para asegurar compatibilidad con versiones recientes de Python (3.14+).

## Requisitos del Sistema

- **Sistema Operativo:** Linux (Fedora 43 probado).
- **Lenguaje:** Python 3.14.
- **Entorno:** Virtualenv (recomendado).

## Dependencias

El proyecto requiere las siguientes librerías de Python:

```bash
pip install mediapipe==0.10.35
pip install opencv-python
pip install numpy
```

## Archivos Necesarios

1.  **`detector_manos.py`**: Script principal de ejecución.
2.  **`hand_landmarker.task`**: Modelo pre-entrenado de MediaPipe (descargado automáticamente durante la configuración inicial).
    *   Si no lo tienes, puedes descargarlo de: [MediaPipe Studio](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task)

## Estructura del Código

El script utiliza `vision.HandLandmarker` configurado en modo `VIDEO` para optimizar el procesamiento de frames de la webcam.

### Configuración Principal:
- `num_hands=1`: Configurado para detectar una sola mano.
- `min_hand_detection_confidence=0.7`: Umbral de confianza para la detección inicial.
- `running_mode=vision.RunningMode.VIDEO`: Optimizado para flujos de video continuos.

## Ejecución

Para iniciar el detector, ejecuta:

```bash
python detector_manos.py
```

### Controles:
- **ESC**: Cierra la aplicación de forma segura.

## Notas de la Migración

La versión anterior basada en `mediapipe.solutions` lanzaba el error:
`AttributeError: module 'mediapipe' has no attribute 'solutions'`

Esto se debe a que las versiones más recientes de MediaPipe para entornos modernos han eliminado esa interfaz en favor de `mediapipe.tasks`. Este proyecto ya implementa la nueva estructura que requiere:
1.  Uso explícito de un archivo `.task`.
2.  Manejo de `timestamps` para el procesamiento de video.
3.  Uso de `mp.Image` en lugar de arreglos directos de NumPy para el procesamiento.
