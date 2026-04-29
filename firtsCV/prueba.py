Created on Mon Nov 4 03:23:41 2019
Author: GROBOT

import cv2
import numpy as np
cap = cv2.VideoCapture(0)
azulBajo = np.array([100, 100, 200], np.uint8)
azulAlto = np.array([125, 255, 255], np.uint8)

while True:
    ret, frame = cap.read()
    if ret==True:
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(frameHSV, azulBajo, azulAlto)
        cv2.imshow('mask', mask)
        cv2.imshow('frame', frame)
        cv2.imshow('Imagen en HSV', frameHSV)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
cap.release()
cv2.destroyAllWindows()