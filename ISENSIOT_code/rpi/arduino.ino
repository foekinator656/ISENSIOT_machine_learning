#include "Servo.h"
#include "max6675.h"

//thermo
int thermoSO = 3;
int thermoCS = 4;
int thermoCLK = 5;

//regulation
int targettemp = 26;
int on = 0;
int heatPin = 2;

//servo
Servo myservo;
int pos = 0;
int servoPin = 13;
int sensorPin = A0;
int sensorValue;
int leftOrRight = 0;

MAX6675 thermocouple(thermoCLK, thermoCS, thermoSO);

#define RUNAVG_T_NSAMPLES 6

typedef struct
{
  float samples[RUNAVG_T_NSAMPLES];  
  int iNewestSample;
  float runningSum;
  
} runAvg_t;

void setup() {
  myservo.attach(servoPin);
  int sensorPin = A0;
  myservo.write(0);
  Serial.begin(9600);
  pinMode (INPUT, sensorPin);
  pinMode(heatPin, OUTPUT);
  delay(500);
}

void loop() {
    int spin = senseSpin();
    float temp = thermocouple.readCelsius();
    regulate(temp);
    String message = String(temp)+" "+String(spin);
    sendAndReceive(message);
    delay(100);
}
