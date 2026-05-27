import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    running_mode=vision.RunningMode.VIDEO
)

detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

print("Iniciando detector de manos (API Tasks). Presiona 'ESC' para salir.")

frame_timestamp_ms = 0

while cap.isOpened():
    exito, frame = cap.read()
    if not exito:
        print("Error durante la captura")
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    frame_timestamp_ms += int(1000 / 30) # Asumiendo 30 fps aprox
    detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)
    
    if detection_result.handedness:
        for idx, hand in enumerate(detection_result.handedness):
            label = hand[0].category_name
            score = hand[0].score
            print(f"Mano Detectada: {label} (Confianza: {score:.2f})")
            
            if detection_result.hand_landmarks:
                landmarks = detection_result.hand_landmarks[idx]
                for lm in landmarks:
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    cv2.imshow('Detector de Manos', frame)
    
    if cv2.waitKey(5) & 0xFF == 27:
        break

detector.close()
cap.release()
cv2.destroyAllWindows()
