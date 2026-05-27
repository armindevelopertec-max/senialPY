import cv2
import mediapipe as objmanos
dibuja_manos = objmanos.solutions.drawing_utils
manos = objmanos.solutions.hands
info_manos = manos.Hands(
    static_image_mode=False,
    max_num_hands=1,  
    min_detection_confidence=0.9
)
cap = cv2.VideoCapture(0)
while cap.isOpened():
    exito, imagen = cap.read()
    if not exito:
        print("Error durante la captura")
        break
    imagen = cv2.cvtColor(cv2.flip(imagen, 1), cv2.COLOR_BGR2RGB)
    detecta_manos_puntos = info_manos.process(imagen)  
    imagen = cv2.cvtColor(imagen, cv2.COLOR_RGB2BGR)
    print("Mano Detectada...:",detecta_manos_puntos.multi_handedness)
    cv2.imshow('Detector de Manos', imagen)
    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
