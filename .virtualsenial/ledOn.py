import sys
import termios
import tty
import serial
import time
import cv2  

print(f"OpenCV versión: {cv2.__version__}")

try:
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    time.sleep(2)
    print("Conectado a /dev/ttyUSB0")
except Exception as e:
    ser = None
    print(f"ADVERTENCIA: No se pudo abrir el puerto serial ({e}).")
    print("Entrando en modo simulación (los comandos no se enviarán).")

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

buffer = ""

print("Comandos: LED ON | LED OFF | ESC/q salir")

while True:
    tecla = getch()

    if tecla == '\x1b' or tecla == 'q':
        print("\nSaliendo...")
        break

    elif tecla == '\r' or tecla == '\n':
        print()

        comando = buffer.strip().upper()

        if comando:
            if ser:
                ser.write((comando + "\n").encode())

                respuesta = ser.readline().decode(errors='ignore').strip()
                print("ESP32:", respuesta)
            else:
                print(f"SIMULACIÓN: Enviando '{comando}' al puerto inexistente.")

        buffer = ""

    elif tecla == '\x7f':
        if len(buffer) > 0:
            buffer = buffer[:-1]
            print('\b \b', end='', flush=True)

    else:
        buffer += tecla
        print(tecla, end='', flush=True)

if ser:
    ser.close()
