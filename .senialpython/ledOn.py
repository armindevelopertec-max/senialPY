import sys
import termios
import tty
import serial
import time

# --- Serial ---
ser = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(2)

# --- getch ---
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# --- buffer ---
buffer = ""

print("Comandos: LED ON | LED OFF | ESC/q salir")

while True:
    tecla = getch()

    # SALIR
    if tecla == '\x1b' or tecla == 'q':
        print("\nSaliendo...")
        break

    # ENTER
    elif tecla == '\r' or tecla == '\n':
        print()

        comando = buffer.strip().upper()

        if comando:
            ser.write((comando + "\n").encode())

            # leer respuesta del ESP32
            respuesta = ser.readline().decode(errors='ignore').strip()
            print("ESP32:", respuesta)

        buffer = ""

    # BACKSPACE (Linux)
    elif tecla == '\x7f':
        if len(buffer) > 0:
            buffer = buffer[:-1]
            print('\b \b', end='', flush=True)

    # CARACTER NORMAL
    else:
        buffer += tecla
        print(tecla, end='', flush=True)

ser.close()
