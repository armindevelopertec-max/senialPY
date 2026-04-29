import msvcrt
import serial
import time

ser = serial.Serial('COM3', 115200)  
time.sleep(2)

buffer = ""

print("Comandos: LED ON | LED OFF | ESC/q salir")

while True:

    tecla = msvcrt.getch()

    try:
        tecla = tecla.decode()
    except:
        continue

    if tecla == '\x1b' or tecla == 'q':
        print("\nSaliendo...")
        break

    elif tecla == '\r':
        print()

        comando = buffer.strip().upper()

        if comando:
            ser.write((comando + "\n").encode())

            respuesta = ser.readline().decode(errors='ignore').strip()
            print("ESP32:", respuesta)

        buffer = ""

    elif tecla == '\x08':
        if len(buffer) > 0:
            buffer = buffer[:-1]
            print('\b \b', end='', flush=True)

    else:
        buffer += tecla
        print(tecla, end='', flush=True)

ser.close()
