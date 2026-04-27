import msvcrt
import serial
import time

# --- Serial ---
ser = serial.Serial('COM3', 115200)  # cambia COM3 por tu puerto
time.sleep(2)

buffer = ""

print("Comandos: LED ON | LED OFF | ESC/q salir")

while True:

    # leer tecla (byte)
    tecla = msvcrt.getch()

    # convertir a string
    try:
        tecla = tecla.decode()
    except:
        continue

    # SALIR
    if tecla == '\x1b' or tecla == 'q':
        print("\nSaliendo...")
        break

    # ENTER
    elif tecla == '\r':
        print()

        comando = buffer.strip().upper()

        if comando:
            ser.write((comando + "\n").encode())

            # leer respuesta ESP32
            respuesta = ser.readline().decode(errors='ignore').strip()
            print("ESP32:", respuesta)

        buffer = ""

    # BACKSPACE (Windows)
    elif tecla == '\x08':
        if len(buffer) > 0:
            buffer = buffer[:-1]
            print('\b \b', end='', flush=True)

    # CARACTER NORMAL
    else:
        buffer += tecla
        print(tecla, end='', flush=True)

ser.close()
