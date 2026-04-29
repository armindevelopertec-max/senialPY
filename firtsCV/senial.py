import cv2
import numpy as np

cap = cv2.VideoCapture(0)

rosadoBajo = np.array([140, 100, 100], np.uint8)
rosadoAlto = np.array([179, 255, 255], np.uint8)
naranjaBajo = np.array([0, 100, 100], np.uint8)
naranjaAlto = np.array([20, 255, 255], np.uint8)

while True:
    ret, frame = cap.read()
    if ret == True:
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask1 = cv2.inRange(frameHSV, rosadoBajo, rosadoAlto)
        mask2 = cv2.inRange(frameHSV, naranjaBajo, naranjaAlto)
        mask = cv2.add(mask1, mask2)
        
        cv2.imshow('mask_rosado', mask1)
        cv2.imshow('mask_naranja', mask2)
        cv2.imshow('mask_final', mask)
        cv2.imshow('frame', frame)
        cv2.imshow('Imagen en HSV', frameHSV)
        
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
