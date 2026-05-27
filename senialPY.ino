#include "BluetoothSerial.h"
#include <math.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled!
#endif

BluetoothSerial SerialBT;

#define IN1 22
#define IN2 19
#define IN3 18
#define IN4 21
#define ENA 25
#define ENB 26

const int C1L = 35;
const int C2L = 34;
const int C1R = 32;
const int C2R = 33;

const int PWM_FREQ = 5000;
const int PWM_RESOLUTION = 8;
const int PWM_DEADBAND = 80;

const int PULSES_PER_REV = 5600;
const float MAX_RPM = 180.0;
const float WHEEL_BASE = 0.15;
const float WHEEL_DIAMETER = 0.065;

const float Kp = 3.8, Ki = 2.5, Kd = 0.15;

const float ALPHA_RPM = 0.5;   
const float ALPHA_DERIV = 0.8; 
const float MAX_ACCEL = 200.0; 
const float K_SYNC = 0.05; 

volatile long nL = 0, nR = 0;
volatile int actL = 0, actR = 0;
volatile unsigned long lastIntL = 0, lastIntR = 0;

bool moviendoObjetivo = false;
double distObjetivo = 0.0;
double angObjetivo = 0.0;
double xInicial = 0.0, yInicial = 0.0, thetaInicial = 0.0;
int modoMovimiento = 0;
double velCruceroLineal = 0.0;
double velCruceroAngular = 0.0;

double velL = 0, velR = 0;
double filteredVelL = 0, filteredVelR = 0;
double prevRawVelL = 0, prevRawVelR = 0;

double targetRPML = 0, targetRPMR = 0;
double rampL = 0, rampR = 0;

float integralL = 0, integralR = 0;
float derivL = 0, derivR = 0;

float derivHistoryL[3] = {0,0,0}, derivHistoryR[3] = {0,0,0};

int pwmL = 0, pwmR = 0;
int dirL = 0, dirR = 0;

double robotX = 0, robotY = 0, robotTheta = 0;

unsigned long lastLoopMicros = 0;
unsigned long lastCmdTime = 0;
unsigned long lastTxTime = 0;

const unsigned long LOOP_PERIOD_US = 20000; 
const unsigned long WATCHDOG_MS = 2000;
const unsigned long TELEMETRY_MS = 150;

void IRAM_ATTR encoderL() {
  unsigned long now = micros();
  if (now - lastIntL < 5) return;
  nL = (digitalRead(C1L) == digitalRead(C2L)) ? nL + 1 : nL - 1;
  lastIntL = now;
}

void IRAM_ATTR encoderR() {
  unsigned long now = micros();
  if (now - lastIntR < 5) return;
  nR = (digitalRead(C1R) == digitalRead(C2R)) ? nR + 1 : nR - 1;
  lastIntR = now;
}


void updateSensors(float dt) {
  static long lastPL = 0, lastPR = 0;
  long pL, pR;

  noInterrupts();
  pL = nL; pR = nR;
  interrupts();

  prevRawVelL = velL;
  prevRawVelR = velR;

  if (dt > 0) {
    velL = ((pL - lastPL) * 60.0) / (dt * PULSES_PER_REV);
    velR = ((pR - lastPR) * 60.0) / (dt * PULSES_PER_REV);
  }

  filteredVelL = ALPHA_RPM * velL + (1.0f - ALPHA_RPM) * filteredVelL;
  filteredVelR = ALPHA_RPM * velR + (1.0f - ALPHA_RPM) * filteredVelR;

  // CÁLCULO DE ODOMETRÍA DIRECTO POR PULSOS (CORREGIDO)
  double dPulsosL = pL - lastPL;
  double dPulsosR = pR - lastPR;

  // Convertir delta de pulsos a metros recorridos por cada rueda
  double dsL = (dPulsosL / (double)PULSES_PER_REV) * M_PI * WHEEL_DIAMETER;
  double dsR = (dPulsosR / (double)PULSES_PER_REV) * M_PI * WHEEL_DIAMETER;

  double dc = (dsL + dsR) / 2.0;
  double dtheta = (dsR - dsL) / WHEEL_BASE;

  robotTheta += dtheta;
  robotTheta = atan2(sin(robotTheta), cos(robotTheta));

  robotX += dc * cos(robotTheta);
  robotY += dc * sin(robotTheta);

  lastPL = pL; lastPR = pR;
}

void updateControl(float dt) {
  if (dt <= 0) return;

  float step = MAX_ACCEL * dt;
  rampL += constrain(targetRPML - rampL, -step, step);
  rampR += constrain(targetRPMR - rampR, -step, step);

  if (abs(targetRPML) < 0.1 && abs(targetRPMR) < 0.1 && abs(filteredVelL) < 0.5 && abs(filteredVelR) < 0.5) {
    pwmL = pwmR = 0;
    integralL *= 0.7; integralR *= 0.7;
    rampL = rampR = 0;
    return;
  }

  float errorL = rampL - filteredVelL;
  float rawDL = -(velL - prevRawVelL) / dt;
  derivHistoryL[2] = derivHistoryL[1]; derivHistoryL[1] = derivHistoryL[0];
  derivHistoryL[0] = rawDL;
  float smoothDL = (derivHistoryL[0] + derivHistoryL[1] + derivHistoryL[2]) / 3.0;
  
  derivL = ALPHA_DERIV * smoothDL + (1.0f - ALPHA_DERIV) * derivL;
  float outL = Kp * errorL + Ki * integralL + Kd * derivL;
  outL = constrain(outL, -255, 255);

  if (abs(outL) < 255 || (outL * errorL < 0)) {
    integralL += errorL * dt;
    integralL = constrain(integralL, -60, 60);
  }

  float errorR = rampR - filteredVelR;
  float rawDR = -(velR - prevRawVelR) / dt;
  derivHistoryR[2] = derivHistoryR[1]; derivHistoryR[1] = derivHistoryR[0];
  derivHistoryR[0] = rawDR;
  float smoothDR = (derivHistoryR[0] + derivHistoryR[1] + derivHistoryR[2]) / 3.0;

  derivR = ALPHA_DERIV * smoothDR + (1.0f - ALPHA_DERIV) * derivR;
  float outR = Kp * errorR + Ki * integralR + Kd * derivR;
  outR = constrain(outR, -255, 255);

  if (abs(outR) < 255 || (outR * errorR < 0)) {
    integralR += errorR * dt;
    integralR = constrain(integralR, -60, 60);
  }

  dirL = (outL >= 0) ? 1 : -1;
  dirR = (outR >= 0) ? 1 : -1;
  pwmL = abs(outL);
  pwmR = abs(outR);

  if (pwmL > 0 && pwmL < PWM_DEADBAND) pwmL = PWM_DEADBAND;
  if (pwmR > 0 && pwmR < PWM_DEADBAND) pwmR = PWM_DEADBAND;
}

void applyMotors() {
  digitalWrite(IN1, (dirL == 1));
  digitalWrite(IN2, (dirL == -1));
  digitalWrite(IN3, (dirR == 1));
  digitalWrite(IN4, (dirR == -1));

  ledcWrite(0, pwmL);
  ledcWrite(1, pwmR);
}

void setVelocity(double linear, double angular) {
  double vL = linear - (angular * WHEEL_BASE / 2.0);
  double vR = linear + (angular * WHEEL_BASE / 2.0);
  targetRPML = constrain((vL * 60.0) / (M_PI * WHEEL_DIAMETER), -MAX_RPM, MAX_RPM);
  targetRPMR = constrain((vR * 60.0) / (M_PI * WHEEL_DIAMETER), -MAX_RPM, MAX_RPM);
}

void processCommand(const char *cmd) {
  lastCmdTime = millis();
  if (cmd[0] == 'V') {
    sscanf(cmd + 2, "%lf,%lf", &targetRPML, &targetRPMR);
  } else if (cmd[0] == 'K') {
    double lin, ang;
    if (sscanf(cmd + 2, "%lf,%lf", &lin, &ang) == 2) {
      setVelocity(lin, ang);
    }
  } else if (cmd[0] == 'D') {
    double d; if (sscanf(cmd + 2, "%lf", &d) == 1) moverCentimetros(d, 0.2);
  } else if (cmd[0] == 'A') {
    double a; if (sscanf(cmd + 2, "%lf", &a) == 1) girarGrados(a, 1.5);
  } else if (cmd[0] == 'S') {
    targetRPML = targetRPMR = 0;
    integralL = integralR = 0;
    rampL = rampR = 0;
  } else if (cmd[0] == 'R') {
    noInterrupts(); nL = nR = 0; interrupts();
    robotX = robotY = robotTheta = 0;
  }
}

void setup() {
  SerialBT.begin("MrRootBot_Ultra_Final");

  pinMode(C1L, INPUT_PULLUP);
  pinMode(C2L, INPUT_PULLUP);
  pinMode(C1R, INPUT_PULLUP);
  pinMode(C2R, INPUT_PULLUP);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(C1L), encoderL, CHANGE);
  attachInterrupt(digitalPinToInterrupt(C1R), encoderR, CHANGE);

  ledcSetup(0, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(1, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(ENA, 0);
  ledcAttachPin(ENB, 1);

  lastLoopMicros = micros();
  lastCmdTime = millis();
}

void loop() {
  unsigned long nowMicros = micros();
  unsigned long nowMillis = millis();

  if (nowMicros - lastLoopMicros >= LOOP_PERIOD_US) {
    float dt = (nowMicros - lastLoopMicros) * 1e-6f;
    lastLoopMicros = nowMicros;

    updateSensors(dt);

    if (moviendoObjetivo) {
      if (modoMovimiento == 1) {
        double distRecorrida = sqrt(pow(robotX - xInicial, 2) + pow(robotY - yInicial, 2));
        if (distRecorrida >= distObjetivo) {
          moviendoObjetivo = false; modoMovimiento = 0; setVelocity(0, 0); lastCmdTime = millis();
        } else {
          // Algoritmo de sincronización activa
          long pL, pR;
          noInterrupts();
          pL = nL; pR = nR;
          interrupts();
          long difPulsos = pL - pR;
          double correccion = difPulsos * K_SYNC;
          
          // Aplica la corrección opuesta a cada rueda para mantener el rumbo
          targetRPML = velCruceroLineal * 60.0 / (M_PI * WHEEL_DIAMETER) - correccion;
          targetRPMR = velCruceroLineal * 60.0 / (M_PI * WHEEL_DIAMETER) + correccion;
          
          // Restringe a los límites máximos permitidos
          targetRPML = constrain(targetRPML, -MAX_RPM, MAX_RPM);
          targetRPMR = constrain(targetRPMR, -MAX_RPM, MAX_RPM);
          
          lastCmdTime = millis();
        }
      } else if (modoMovimiento == 2) {
        double deltaTheta = robotTheta - thetaInicial;
        deltaTheta = atan2(sin(deltaTheta), cos(deltaTheta));
        if (abs(deltaTheta) >= angObjetivo) {
          moviendoObjetivo = false; modoMovimiento = 0; setVelocity(0, 0); lastCmdTime = millis();
        } else {
          setVelocity(0.0, velCruceroAngular); lastCmdTime = millis();
        }
      }
    }

    updateControl(dt);
    applyMotors();
  }

  if (nowMillis - lastCmdTime > WATCHDOG_MS) {
    targetRPML = 0; targetRPMR = 0;
  }

  while (SerialBT.available()) {
    static char buf[64];
    static int idx = 0;
    char c = SerialBT.read();
    if (c == '\n' || c == '\r') {
      if (idx > 0) {
        buf[idx] = '\0';
        processCommand(buf);
        idx = 0;
      }
    } else if (idx < 63) {
      buf[idx++] = c;
    }
  }

  /* 
  if (nowMillis - lastTxTime > TELEMETRY_MS) {
    lastTxTime = nowMillis;
    long pL, pR;
    noInterrupts();
    pL = nL; pR = nR;
    interrupts();
    SerialBT.printf("Posicion_X:%.2f Posicion_Y:%.2f Orientacion_Theta:%.2f RPM_Izq:%.1f RPM_Der:%.1f Pulsos_Izq:%ld Pulsos_Der:%ld\n",
                    robotX, robotY, robotTheta,
                    filteredVelL, filteredVelR, pL, pR);
  }
  */
}

void moverCentimetros(double cm, double velLineal) {
  xInicial = robotX; yInicial = robotY;
  distObjetivo = abs(cm) / 100.0;
  velCruceroLineal = (cm >= 0) ? velLineal : -velLineal;
  modoMovimiento = 1;
  moviendoObjetivo = true;
}

void girarGrados(double grados, double velAngular) {
  thetaInicial = robotTheta;
  angObjetivo = abs(grados * M_PI / 180.0);
  velCruceroAngular = (grados >= 0) ? velAngular : -velAngular;
  modoMovimiento = 2;
  moviendoObjetivo = true;
}

