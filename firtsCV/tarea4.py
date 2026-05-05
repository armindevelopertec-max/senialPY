import cv2
import numpy as np


cap = cv2.VideoCapture(0)

azulBajo = np.array([100, 100, 20], np.uint8)
azulAlto = np.array([125, 255, 255], np.uint8)


def distancia(p1, p2):
    return np.linalg.norm(p1 - p2)


def angulo(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)

    if denom == 0:
        return 180.0

    coseno = np.clip(np.dot(v1, v2) / denom, -1.0, 1.0)
    return np.degrees(np.arccos(coseno))


def clasificar_figura(approx, contorno):
    vertices = len(approx)

    if vertices == 3:
        return "Triangulo"

    if vertices == 4:
        puntos = approx.reshape(4, 2).astype("float32")

        lados = [
            distancia(puntos[i], puntos[(i + 1) % 4])
            for i in range(4)
        ]
        angulos = [
            angulo(puntos[(i - 1) % 4], puntos[i], puntos[(i + 1) % 4])
            for i in range(4)
        ]

        lado_promedio = sum(lados) / 4.0
        lados_similares = all(
            abs(lado - lado_promedio) / lado_promedio < 0.15
            for lado in lados
        )
        angulos_rectos = all(abs(a - 90) < 15 for a in angulos)
        lados_opuestos_similares = (
            abs(lados[0] - lados[2]) / max(lados[0], lados[2]) < 0.15
            and abs(lados[1] - lados[3]) / max(lados[1], lados[3]) < 0.15
        )

        if angulos_rectos and lados_similares:
            return "Cuadrado"

        if angulos_rectos and lados_opuestos_similares:
            return "Rectangulo"

        if lados_similares:
            return "Rombo"

        return "Cuadrilatero"

    perimetro = cv2.arcLength(contorno, True)
    area = cv2.contourArea(contorno)

    if perimetro == 0:
        return "Desconocida"

    circularidad = 4 * np.pi * area / (perimetro * perimetro)

    if circularidad > 0.82 and vertices >= 5:
        return "Circulo"

    return "Figura"


while True:
    ret, frame = cap.read()

    if ret == True:
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(frameHSV, azulBajo, azulAlto)

        (contornos, _) = cv2.findContours(
            mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE
        )

        for c in contornos:
            area = cv2.contourArea(c)

            if area > 300:
                M = cv2.moments(c)

                if (M["m00"] == 0):
                    M["m00"] = 1

                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])

                perimetro = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * perimetro, True)
                vertices = len(approx)
                figura = clasificar_figura(approx, c)

                font = cv2.FONT_HERSHEY_SIMPLEX

                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    "{},{}".format(x, y),
                    (x + 10, y),
                    font,
                    0.75,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )
                cv2.drawContours(frame, [approx], 0, (255, 0, 0), 3)
                cv2.putText(
                    frame,
                    f"Vertices: {vertices}",
                    (x - 60, y - 20),
                    font,
                    0.6,
                    (0, 255, 255),
                    2,
                )
                cv2.putText(
                    frame,
                    figura,
                    (x - 60, y - 50),
                    font,
                    0.8,
                    (0, 0, 255),
                    2,
                )

        cv2.imshow("maskAzul", frameHSV)
        cv2.imshow("frame", frame)
        cv2.imshow("contornos", mask)

    if cv2.waitKey(1) & 0xFF == ord("s"):
        break

cap.release()
cv2.destroyAllWindows()
