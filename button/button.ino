#include "LowPower.h"
#include <EEPROM.h>

#define DEFAULT_SLEEP 8

#define L 13
#define R 10
#define CPU_FACTOR 2
int addr = 0;


void up(int ms) {
  EEPROM.write(addr, 1);
  digitalWrite(L, LOW);
  digitalWrite(R, HIGH);
  delay(ms);
  digitalWrite(L, LOW);
  digitalWrite(R, LOW);
}

void down(int ms) {
  EEPROM.write(addr, 0);
  digitalWrite(L, HIGH);
  digitalWrite(R, LOW);
  delay(ms);
  digitalWrite(L, LOW);
  digitalWrite(R, LOW);
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
  CLKPR = 0x80; // (1000 0000) enable change in clock frequency
  CLKPR = 0x01; // (0000 0001) use clock division factor 2 to reduce the frequency from 16 MHz to 8 MHz
  ADCSRA |= (1 << ADEN);
  pinMode(L, OUTPUT);
  pinMode(R, OUTPUT);
  int turnedon = 1;
  int isUp = EEPROM.read(addr);
  if (isUp == 0) {
    up(248 / CPU_FACTOR);
  }
  sleepOne(1);
}

void loop() {
  down(300 / CPU_FACTOR);
  sleepFor(210);
  up(248 / CPU_FACTOR);
  sleepFor(1800);
}
