import cv2
import mediapipe as objmanos

dibuja_manos = objmanos.solutions.drawing_utils
manos = objmanos.solutions.hands

info_manos = manos.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    exito, imagen = cap.read()
    if not exito:
        break

    alto, ancho, _ = imagen.shape
    imagen = cv2.cvtColor(cv2.flip(imagen, 1), cv2.COLOR_BGR2RGB)
    resultado = info_manos.process(imagen)
    imagen = cv2.cvtColor(imagen, cv2.COLOR_RGB2BGR)

    if resultado.multi_hand_landmarks:
        for mano in resultado.multi_hand_landmarks:
            # Punto 8 es la punta del dedo indice
            punto = mano.landmark[8]
            
            # Convertir coordenadas normalizadas a pixeles
            px = int(punto.x * ancho)
            py = int(punto.y * alto)
            pz = punto.z # Profundidad relativa

            # Dibujar un circulo en la punta del dedo
            cv2.circle(imagen, (px, py), 10, (0, 255, 0), -1)
            
            # Mostrar coordenadas en pantalla
            cv2.putText(imagen, f"X:{px} Y:{py} Z:{pz:.2f}", (px + 10, py), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('Seguimiento de un Dedo', imagen)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
