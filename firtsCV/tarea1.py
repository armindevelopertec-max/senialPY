import cv2
import numpy as np

cap = cv2.VideoCapture(0)

azulBajo = np.array([100,100,20], np.uint8)
azulAlto = np.array([125,255,255], np.uint8)

while True:
    ret, frame = cap.read()

    if ret == True:
    
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask= cv2.inRange(frameHSV, azulBajo, azulAlto)

        (contornos, _) = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        for c in contornos:
        
            area= cv2.contourArea(c)

            if area > 1000:
            
                nuevoContorno = cv2.convexHull(c)

                cv2.drawContours(frame, [nuevoContorno], -1, (0,255,0), 3)

                cv2.drawContours(frame, [c], -1, (0,0,255), 1)

    cv2.imshow('frame', frame)

    cv2.imshow('contornos', mask)

    if cv2.waitKey(1) & 0xFF == ord('s'):
         
         break
cap.release()
cv2.destroyAllWindows()      
    
            