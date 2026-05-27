import cv2
import mediapipe as objmanos
dibuja_mano = objmanos.solutions.drawing_utils
info_manos = objmanos.solutions.hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.9
)
cap = cv2.VideoCapture(0)
while cap.isOpened():
    exito, imagen = cap.read()
    if not exito:
        break
    imagen = cv2.flip(imagen, 1)
    rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    resultados = info_manos.process(rgb)
    alto, ancho, _ = imagen.shape
    if resultados.multi_hand_landmarks:
        for mano in resultados.multi_hand_landmarks:
            menique = mano.landmark[
                objmanos.solutions.hands.HandLandmark.INDEX_FINGER_PIP
            ]
            x, y = int(menique.x * ancho), int(menique.y * alto)
            cv2.circle(imagen, (x, y), 7, (0, 255, 0), 2)
            print(f"Menique - x: {x}, y: {y}")
    cv2.imshow('Detector de manos', imagen)
    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()