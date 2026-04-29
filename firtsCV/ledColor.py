import cv2
import numpy as np
import serial
import time

try:
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    time.sleep(2)
    print("Conexión serial lista")
except Exception as e:
    print(f"Error: {e}")
    exit()

azulBajo = np.array([110, 100, 20], np.uint8)
azulAlto = np.array([111, 255, 255], np.uint8)

verdeBajo = np.array([36, 100, 100], np.uint8)
verdeAlto = np.array([85, 255, 255], np.uint8)

naranjaBajo = np.array([15, 100, 100], np.uint8)
naranjaAlto = np.array([22, 255, 255], np.uint8)

amarilloBajo = np.array([28, 100, 100], np.uint8)
amarilloAlto = np.array([33, 255, 255], np.uint8)

azul_on = False
verde_on = False
naranja_on = False
amarillo_on = False

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    maskAzul = cv2.inRange(frameHSV, azulBajo, azulAlto)
    maskVerde = cv2.inRange(frameHSV, verdeBajo, verdeAlto)
    maskNaranja = cv2.inRange(frameHSV, naranjaBajo, naranjaAlto)
    maskAmarillo = cv2.inRange(frameHSV, amarilloBajo, amarilloAlto)
    
    if cv2.countNonZero(maskAzul) > 5000:
        if not azul_on:
            ser.write(b"AZUL ON\n")
            azul_on = True
    else:
        if azul_on:
            ser.write(b"AZUL OFF\n")
            azul_on = False

    if cv2.countNonZero(maskVerde) > 5000:
        if not verde_on:
            ser.write(b"VERDE ON\n")
            verde_on = True
    else:
        if verde_on:
            ser.write(b"VERDE OFF\n")
            verde_on = False

    if cv2.countNonZero(maskNaranja) > 5000:
        if not naranja_on:
            ser.write(b"NARANJA ON\n")
            naranja_on = True
    else:
        if naranja_on:
            ser.write(b"NARANJA OFF\n")
            naranja_on = False

    if cv2.countNonZero(maskAmarillo) > 5000:
        if not amarillo_on:
            ser.write(b"AMARILLO ON\n")
            amarillo_on = True
    else:
        if amarillo_on:
            ser.write(b"AMARILLO OFF\n")
            amarillo_on = False

    cv2.imshow('Original', frame)
    cv2.imshow('Mascara Azul', maskAzul)
    cv2.imshow('Mascara Verde', maskVerde)
    cv2.imshow('Mascara Naranja', maskNaranja)
    cv2.imshow('Mascara Amarillo', maskAmarillo)
    
    if cv2.waitKey(1) & 0xFF == ord('s'):
        break

ser.write(b"OFF ALL\n")
cap.release()
cv2.destroyAllWindows()
ser.close()
