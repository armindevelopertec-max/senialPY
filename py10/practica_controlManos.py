# control_manos_robot_bt.py
# Requiere:
# pip install opencv-python mediapipe pybluez
#
# Gestos:
# 👍 Pulgar arriba        -> AVANZAR
# 👎 Pulgar abajo         -> RETROCEDER
# 👈 Índice + pulgar izq  -> GIRAR IZQUIERDA
# 👉 Índice + pulgar der  -> GIRAR DERECHA
# ✊ Puño cerrado         -> STOP
#
# Compatible con mano izquierda y derecha.
# Envía comandos Bluetooth al ESP32.

import cv2
import mediapipe as mp
import socket
import math
import time
import sys
import argparse

# =========================
# CONFIGURACIÓN Y ARGUMENTOS
# =========================
parser = argparse.ArgumentParser(description="Control de Robot por Gestos")
parser.add_argument("--mock", action="store_true", help="Modo emulación (sin Bluetooth)")
parser.add_argument("--mac", type=str, default="CC:7B:5C:23:4C:E2", help="Dirección MAC del ESP32")
args = parser.parse_args()

NOMBRE_BT = "MrRootBot_Ultra_Final"
MAC_ESP32 = args.mac 
PUERTO = 1
MOCK_MODE = args.mock

sock = None

if not MOCK_MODE:
    print(f"Intentando conectar a {NOMBRE_BT} ({MAC_ESP32})...")
    try:
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        sock.connect((MAC_ESP32, PUERTO))
        print("¡Bluetooth conectado!")
    except Exception as e:
        print(f"Error al conectar Bluetooth: {e}")
        print("Iniciando en modo MOCK automáticamente...")
        MOCK_MODE = True
else:
    print("Modo EMULACIÓN activado.")

# =========================
# MEDIAPIPE
# =========================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

cap = cv2.VideoCapture(0)

comando_persistente = "S"
texto_estado = "STOP"

# =========================
# FUNCIONES
# =========================
def enviar_persistente(comando):
    """Envía el comando actual en cada iteración del loop"""
    if MOCK_MODE:
        # En mock solo printeamos si cambia para no saturar la terminal, 
        # pero la lógica real enviará siempre.
        return

    try:
        sock.send((comando + "\n").encode('utf-8'))
    except Exception as e:
        print("Error de comunicación:", e)

# =========================
# LOOP PRINCIPAL
# =========================
while cap.isOpened():
    ok, frame = cap.read()
    if not ok: break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(rgb)

    if resultado.multi_hand_landmarks:
        for mano in resultado.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, mano, mp_hands.HAND_CONNECTIONS)
            puntos = mano.landmark

            # Puntos clave (TIP y PIP/IP)
            p = {
                'pulgar_tip': puntos[4], 'pulgar_ip': puntos[3],
                'indice_tip': puntos[8], 'indice_pip': puntos[6],
                'medio_tip': puntos[12], 'medio_pip': puntos[10],
                'anular_tip': puntos[16], 'anular_pip': puntos[14],
                'menique_tip': puntos[20], 'menique_pip': puntos[18]
            }

            # Lógica de dedos extendidos (más robusta)
            pulgar_up = p['pulgar_tip'].y < p['pulgar_ip'].y
            indice_up = p['indice_tip'].y < p['indice_pip'].y
            medio_up = p['medio_tip'].y < p['medio_pip'].y
            anular_up = p['anular_tip'].y < p['anular_pip'].y
            menique_up = p['menique_tip'].y < p['menique_pip'].y
            
            # PALMA ABIERTA (Saludo) -> STOP
            # Si todos los dedos están hacia arriba
            palma_abierta = indice_up and medio_up and anular_up and menique_up
            
            # PUÑO (Opcional, ahora podrías usarlo para otra cosa o ignorarlo)
            punio = not (indice_up or medio_up or anular_up or menique_up)
            
            pulgar_down = p['pulgar_tip'].y > p['pulgar_ip'].y
            dx_pulgar = p['pulgar_tip'].x - p['pulgar_ip'].x
            
            # Direcciones del índice para giros
            dx_indice = p['indice_tip'].x - p['indice_pip'].x
            # Consideramos que apunta a un lado si la diferencia en X es mayor que en Y
            apunta_lado = abs(dx_indice) > abs(p['indice_tip'].y - p['indice_pip'].y)

            # ASIGNACIÓN DE COMANDO PERSISTENTE (Prioridad: STOP > GIROS > ADELANTE/ATRAS)
            if palma_abierta:
                comando_persistente = "S"
                texto_estado = "STOP (Palma)"
            
            # Giros (Independientes del pulgar)
            elif apunta_lado and dx_indice < -0.05:
                comando_persistente = "K:0,1.8"
                texto_estado = "IZQUIERDA"
            elif apunta_lado and dx_indice > 0.05:
                comando_persistente = "K:0,-1.8"
                texto_estado = "DERECHA"
            
            # Movimiento lineal
            elif pulgar_up and not indice_up:
                comando_persistente = "K:0.25,0"
                texto_estado = "ADELANTE"
            elif pulgar_down and not indice_up:
                comando_persistente = "K:-0.20,0"
                texto_estado = "ATRAS"

    # ENVÍO CONSTANTE (Fuera del if de detección de manos si quieres que mantenga el último comando)
    # O dentro si quieres que se detenga al quitar la mano. 
    # Siguiendo tu lógica de "flecha", lo mantenemos persistente.
    enviar_persistente(comando_persistente)

    # UI
    color = (0, 0, 255) if comando_persistente == "S" else (0, 255, 0)
    cv2.putText(frame, f"COMANDO: {texto_estado}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    if MOCK_MODE:
        cv2.putText(frame, "MODO MOCK ACTIVADO", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

    cv2.imshow("Robot Gestos Persistente", frame)
    if cv2.waitKey(1) == 27: break
    time.sleep(0.01) # Pequeño delay para no saturar el CPU


cap.release()
if sock: sock.close()
cv2.destroyAllWindows()

