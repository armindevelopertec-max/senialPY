import cv2
import numpy as np
import mediapipe as objmanos

manos = objmanos.solutions.hands
info_manos = manos.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

cap = cv2.VideoCapture(0)

# Lienzo para dibujar (fondo negro, mismo tamaño que la cámara)
lienzo = None

# Color del trazo (Verde) y grosor
color = (0, 255, 0)
grosor = 5

# Posición anterior para unir puntos con líneas
x_ant, y_ant = 0, 0

while cap.isOpened():
    exito, imagen = cap.read()
    if not exito: break

    imagen = cv2.flip(imagen, 1)
    alto, ancho, _ = imagen.shape

    # Inicializar el lienzo en el primer frame
    if lienzo is None:
        lienzo = np.zeros((alto, ancho, 3), dtype=np.uint8)

    rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    resultado = info_manos.process(rgb)

    if resultado.multi_hand_landmarks:
        for mano in resultado.multi_hand_landmarks:
            # Obtener coordenadas del índice (8) y medio (12)
            indice = mano.landmark[8]
            medio = mano.landmark[12]

            x = int(indice.x * ancho)
            y = int(indice.y * alto)
            
            # Calcular distancia entre índice y medio para "activar" el dibujo
            # Si están cerca (como un pellizco), dibujamos
            distancia = np.hypot(indice.x - medio.x, indice.y - medio.y)

            if distancia < 0.05: # Umbral para detectar dedos juntos
                if x_ant == 0 and y_ant == 0:
                    x_ant, y_ant = x, y
                
                cv2.line(lienzo, (x_ant, y_ant), (x, y), color, grosor)
                x_ant, y_ant = x, y
            else:
                # Si separamos los dedos, reiniciamos el trazo
                x_ant, y_ant = 0, 0

    # Combinar la imagen de la cámara con el lienzo
    # Convertimos el lienzo a gris para crear una máscara
    lienzo_gris = cv2.cvtColor(lienzo, cv2.COLOR_BGR2GRAY)
    _, mascara = cv2.threshold(lienzo_gris, 10, 255, cv2.THRESH_BINARY)
    mascara_inv = cv2.bitwise_not(mascara)

    # Agregamos el lienzo a la imagen original
    img_fondo = cv2.bitwise_and(imagen, imagen, mask=mascara_inv)
    imagen_final = cv2.add(img_fondo, lienzo)

    cv2.imshow('Pizarra Virtual (Junta Indice y Medio para dibujar)', imagen_final)

    tecla = cv2.waitKey(5) & 0xFF
    if tecla == 27: break
    elif tecla == ord('c'): # Tecla 'c' para limpiar lienzo
        lienzo = np.zeros((alto, ancho, 3), dtype=np.uint8)

cap.release()
cv2.destroyAllWindows()
