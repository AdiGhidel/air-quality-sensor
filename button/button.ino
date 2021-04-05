#include "LowPower.h"
#define DEFAULT_SLEEP 8

#define L 13
#define R 10
#define CPU_FACTOR 2
void setup() {
  CLKPR = 0x80; // (1000 0000) enable change in clock frequency
  CLKPR = 0x01; // (0000 0001) use clock division factor 2 to reduce the frequency from 16 MHz to 8 MHz
  ADCSRA |= (1 << ADEN);
  pinMode(L, OUTPUT);
  pinMode(R, OUTPUT);

}

void sleepFor(int seconds) {
  int counter = 0;
  while (counter < seconds) {
    counter += DEFAULT_SLEEP;
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }
}

void up(int ms) {
  digitalWrite(L, LOW);
  digitalWrite(R, HIGH);
  delay(ms);
  digitalWrite(L, LOW);
  digitalWrite(R, LOW);
}

void down(int ms) {
  digitalWrite(L, HIGH);
  digitalWrite(R, LOW);
  delay(ms);
  digitalWrite(L, LOW);
  digitalWrite(R, LOW);
}

void loop() {
  up(248 / CPU_FACTOR);
  sleepFor(1800);
  down(285 / CPU_FACTOR);
  sleepFor(210);
}
