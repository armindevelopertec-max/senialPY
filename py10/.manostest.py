# Importa OpenCV
# Se usa para trabajar con la cámara y mostrar imágenes
import cv2

# Importa MediaPipe con un alias llamado "objmanos"
import mediapipe as objmanos

 
# ================================
# UTILIDADES DE DIBUJO
# ================================

# Carga las herramientas para dibujar puntos y conexiones
# de la mano sobre la imagen
dibuja_manos = objmanos.solutions.drawing_utils


# ================================
# MÓDULO DE DETECCIÓN DE MANOS
# ================================

# Carga el módulo Hands de MediaPipe
manos = objmanos.solutions.hands


# ================================
# CONFIGURACIÓN DEL DETECTOR
# ================================

# Crea el detector de manos
info_manos = manos.Hands(

    # False = modo video en tiempo real
    # True = analiza cada frame como imagen independiente
    static_image_mode=False,

    # Máximo número de manos a detectar
    max_num_hands=2,

    # Confianza mínima para detectar la mano
    # 0.9 = 90%
    min_detection_confidence=0.9
)


# ================================
# ABRIR LA CÁMARA
# ================================

# 0 = cámara principal
cap = cv2.VideoCapture(0)


# ================================
# BUCLE PRINCIPAL
# ================================

# Mientras la cámara siga abierta
while cap.isOpened():

    # Lee un frame de la cámara
    # exito -> True/False
    # imagen -> frame capturado
    exito, imagen = cap.read()

    # Si hubo error al capturar
    if not exito:
        print("Error durante la captura")
        break


    # ================================
    # PREPROCESAMIENTO
    # ================================

    # cv2.flip(imagen,1)
    # Invierte la imagen horizontalmente tipo espejo

    # cv2.cvtColor(..., cv2.COLOR_BGR2RGB)
    # Convierte la imagen de BGR a RGB
    # porque MediaPipe trabaja en RGB
    imagen = cv2.cvtColor(
        cv2.flip(imagen, 1),
        cv2.COLOR_BGR2RGB
    )


    # ================================
    # DETECCIÓN DE MANOS
    # ================================

    # Analiza la imagen y detecta manos
    detecta_manos_puntos = info_manos.process(imagen)


    # ================================
    # CONVERTIR DE NUEVO A BGR
    # ================================

    # OpenCV muestra imágenes en BGR
    # por eso volvemos a convertir
    imagen = cv2.cvtColor(
        imagen,
        cv2.COLOR_RGB2BGR
    )


    # ================================
    # MOSTRAR INFORMACIÓN EN CONSOLA
    # ================================

    # Imprime si detectó mano izquierda o derecha
    print(
        "Mano Detectada...:",
        detecta_manos_puntos.multi_handedness
    )


    # ================================
    # DIBUJAR LANDMARKS (OPCIONAL)
    # ================================

    # Si detectó puntos de la mano
    if detecta_manos_puntos.multi_hand_landmarks:

        # Recorre cada mano detectada
        for mano in detecta_manos_puntos.multi_hand_landmarks:

            # Dibuja puntos y conexiones
            dibuja_manos.draw_landmarks(

                # Imagen donde dibujar
                imagen,

                # Mano detectada
                mano,

                # Conexiones entre puntos
                manos.HAND_CONNECTIONS
            )


    # ================================
    # MOSTRAR VIDEO
    # ================================

    # Muestra la ventana con la cámara
    cv2.imshow(
        'Detector de Manos',
        imagen
    )


    # ================================
    # SALIR CON ESC
    # ================================

    # waitKey(5) espera 5 milisegundos

    # 27 = tecla ESC
    if cv2.waitKey(5) & 0xFF == 27:
        break


# ================================
# LIBERAR RECURSOS
# ================================

# Libera la cámara
cap.release()

# Cierra todas las ventanas
cv2.destroyAllWindows()