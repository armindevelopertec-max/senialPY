# control_manos_robot_bt.py
import cv2
import mediapipe as mp
import socket
import math
import time
import sys
import argparse

# =========================
# CONFIGURACIÓN Y FILTROS
# =========================
parser = argparse.ArgumentParser(description="Control de Robot por Gestos")
parser.add_argument("--mock", action="store_true", help="Modo emulación (sin Bluetooth)")
parser.add_argument("--mac", type=str, default="CC:7B:5C:23:4C:E2", help="Dirección MAC del ESP32")
args = parser.parse_args()

NOMBRE_BT = "MrRootBot"
MAC_ESP32 = args.mac 
PUERTO = 1
MOCK_MODE = args.mock

UMBRAL_CONFIRMACION = 3  # Fotogramas seguidos para cambiar de comando
contadores = {"STOP": 0, "IZQ": 0, "DER": 0, "UP": 0, "DOWN": 0}

comando_persistente = "S"
texto_estado = "STOP"

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
# MEDIAPIPE Y CÁMARA
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

# =========================
# FUNCIONES
# =========================
def enviar_persistente(comando):
    """Envía el comando actual en cada iteración del loop"""
    if MOCK_MODE:
        return

    try:
        sock.send((comando + "\n").encode('utf-8'))
    except Exception as e:
        print("Error de comunicación:", e)

def actualizar_comando(nuevo_comando, nuevo_texto, clave_contador):
    """Solo cambia el comando si se mantiene varios fotogramas"""
    global comando_persistente, texto_estado
    
    # Reiniciar los otros contadores
    for k in contadores:
        if k != clave_contador:
            contadores[k] = 0
            
    contadores[clave_contador] += 1
    
    if contadores[clave_contador] >= UMBRAL_CONFIRMACION:
        comando_persistente = nuevo_comando
        texto_estado = nuevo_texto

# =========================
# LOOP PRINCIPAL
# =========================
while cap.isOpened():
    ok, frame = cap.read()
    if not ok: break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(rgb)

    gesto_detectado_en_frame = False

    if resultado.multi_hand_landmarks:
        # Tomamos solo la primera mano para evitar interferencias
        mano = resultado.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, mano, mp_hands.HAND_CONNECTIONS)
        puntos = mano.landmark

        p = {
            'pulgar_tip': puntos[4], 'pulgar_ip': puntos[3],
            'indice_tip': puntos[8], 'indice_pip': puntos[6],
            'medio_tip': puntos[12], 'medio_pip': puntos[10],
            'anular_tip': puntos[16], 'anular_pip': puntos[14],
            'menique_tip': puntos[20], 'menique_pip': puntos[18]
        }

        # 1. ESTADO DE DEDOS
        indice_up = p['indice_tip'].y < p['indice_pip'].y
        pulgar_up = p['pulgar_tip'].y < p['pulgar_ip'].y
        pulgar_down = p['pulgar_tip'].y > p['pulgar_ip'].y
        
        # 2. DETECCIÓN DE GIROS (Prioridad Alta - Solo mira el Índice)
        dx_indice = p['indice_tip'].x - p['indice_pip'].x
        dy_indice = p['indice_tip'].y - p['indice_pip'].y
        apunta_horizontal = abs(dx_indice) > abs(dy_indice) * 1.5

        # 3. PALMA ABIERTA (Solo si todos están arriba)
        dedos_arriba = sum([p[tip].y < p[pip].y for tip, pip in [
            ('indice_tip', 'indice_pip'), ('medio_tip', 'medio_pip'), 
            ('anular_tip', 'anular_pip'), ('menique_tip', 'menique_pip')
        ]])

        # --- LÓGICA DE DECISIÓN "BLOQUEANTE" ---
        
        if dedos_arriba >= 3: # Si hay 3 o más dedos arriba, es probable que sea STOP
            actualizar_comando("S", "STOP (Palma)", "STOP")
            gesto_detectado_en_frame = True

        elif apunta_horizontal and abs(dx_indice) > 0.06:
            if dx_indice < 0:
                actualizar_comando("K:0,1.8", "IZQUIERDA", "IZQ")
            else:
                actualizar_comando("K:0,-1.8", "DERECHA", "DER")
            gesto_detectado_en_frame = True

        elif pulgar_up and not indice_up:
            actualizar_comando("K:0.25,0", "ADELANTE", "UP")
            gesto_detectado_en_frame = True

        elif pulgar_down and not indice_up:
            actualizar_comando("K:-0.20,0", "ATRAS", "DOWN")
            gesto_detectado_en_frame = True

    if not gesto_detectado_en_frame:
        # Si no detecta nada claro, vamos reseteando contadores poco a poco
        for k in contadores: contadores[k] = max(0, contadores[k] - 1)

    # ENVÍO CONSTANTE
    enviar_persistente(comando_persistente)

    # UI MEJORADA
    color = (0, 0, 255) if comando_persistente == "S" else (0, 255, 0)
    cv2.rectangle(frame, (10, 10), (400, 60), (0,0,0), -1)
    cv2.putText(frame, f"ROBOT: {texto_estado}", (20, 45), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Control Robusto - Fedora", frame)
    if cv2.waitKey(1) == 27: break
    time.sleep(0.01)

cap.release()
if sock: sock.close()
cv2.destroyAllWindows()
