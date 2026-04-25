const int ledPin = 2;

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {

    String comando = Serial.readStringUntil('\n');
    comando.trim();  // limpia espacios y \r

    if (comando == "LED ON") {
      digitalWrite(ledPin, HIGH);
      Serial.println("OK LED ON");   // respuesta
    }
    else if (comando == "LED OFF") {
      digitalWrite(ledPin, LOW);
      Serial.println("OK LED OFF");  // respuesta
    }
    else {
      Serial.println("ERROR");       // comando inválido
    }
  }
}