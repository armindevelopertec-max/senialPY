const int pinAzul = 21;
const int pinVerde = 22;
const int pinNaranja = 18;
const int pinAmarillo = 19;

void setup() {
  Serial.begin(115200);
  
  pinMode(pinAzul, OUTPUT);
  pinMode(pinVerde, OUTPUT);
  pinMode(pinNaranja, OUTPUT);
  pinMode(pinAmarillo, OUTPUT);

  digitalWrite(pinAzul, LOW);
  digitalWrite(pinVerde, LOW);
  digitalWrite(pinNaranja, LOW);
  digitalWrite(pinAmarillo, LOW);
  
  Serial.println("Sistema listo. Esperando comandos (Ej: ROJO ON, VERDE OFF...)");
}

void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    comando.toUpperCase();

    if (comando == "AZUL ON") {
      digitalWrite(pinAzul, HIGH);
      Serial.println("OK AZUL ON");
    } else if (comando == "AZUL OFF") {
      digitalWrite(pinAzul, LOW);
      Serial.println("OK AZUL OFF");
    } else if (comando == "VERDE ON") {
      digitalWrite(pinVerde, HIGH);
      Serial.println("OK VERDE ON");
    } else if (comando == "VERDE OFF") {
      digitalWrite(pinVerde, LOW);
      Serial.println("OK VERDE OFF");
    } else if (comando == "NARANJA ON") {
      digitalWrite(pinNaranja, HIGH);
      Serial.println("OK NARANJA ON");
    } else if (comando == "NARANJA OFF") {
      digitalWrite(pinNaranja, LOW);
      Serial.println("OK NARANJA OFF");
    } else if (comando == "AMARILLO ON") {
      digitalWrite(pinAmarillo, HIGH);
      Serial.println("OK AMARILLO ON");
    } else if (comando == "AMARILLO OFF") {
      digitalWrite(pinAmarillo, LOW);
      Serial.println("OK AMARILLO OFF");
    } else if (comando == "OFF ALL") {
      digitalWrite(pinAzul, LOW);
      digitalWrite(pinVerde, LOW);
      digitalWrite(pinNaranja, LOW);
      digitalWrite(pinAmarillo, LOW);
      Serial.println("OK TODO APAGADO");
    } else {
      Serial.println("ERROR: Comando desconocido");
    }
  }
}
