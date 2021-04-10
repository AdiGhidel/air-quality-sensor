#include "LowPower.h"
#include <EEPROM.h>

#define DEFAULT_SLEEP 8

#define L 2
#define R 13
#define CPU_FACTOR 2
int addr = 0;

#define DOWN 320
#define UP 280
void up(int ms) {
  EEPROM.write(addr, 1);
  digitalWrite(L, LOW);
  digitalWrite(R, HIGH);
  delay(ms);
  digitalWrite(L, LOW);
  digitalWrite(R, LOW);
  delay(100);
}

void down(int ms) {
  EEPROM.write(addr, 0);
  digitalWrite(L, HIGH);
  digitalWrite(R, LOW);
  delay(ms);
  digitalWrite(L, LOW);
  digitalWrite(R, LOW);
  delay(100);
}

void sleepFor(int seconds) {
  int counter = 0;
  while (counter < seconds) {
    counter += DEFAULT_SLEEP;
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }
}
void sleepOne(int seconds) {
  int counter = 0;
  while (counter < seconds) {
    counter += 1;
    LowPower.powerDown(SLEEP_1S, ADC_OFF, BOD_OFF);
  }
}

void setup() {
  delay(3000);
  CLKPR = 0x80; // (1000 0000) enable change in clock frequency
  CLKPR = 0x01; // (0000 0001) use clock division factor 2 to reduce the frequency from 16 MHz to 8 MHz
  ADCSRA |= (1 << ADEN);
  pinMode(L, OUTPUT);
  pinMode(R, OUTPUT);
  int isUp = EEPROM.read(addr);
  if (isUp == 0) {
    Serial.println("going up");
    up(UP / CPU_FACTOR);
  }
  delay(1000);
}

void loop() {
  Serial.println("started loop");
  down(DOWN / CPU_FACTOR);
  sleepFor(210);
  Serial.println("going down");
  up(UP / CPU_FACTOR);
  sleepFor(1800);
}
