#include "sw_uart.h"

due_sw_uart uart;

void setup() {
  Serial.begin(9600);
  pinMode(4,OUTPUT);
  digitalWrite(4, HIGH);
  delay(2000);
}

void loop() {
  // 'a' -> 01100001
  int binary[] = {0, 1, 1, 0, 0, 0, 0, 1};

  digitalWrite(4, LOW); // start bit
  wait_T();

  digitalWrite(4, HIGH); // data bit
  wait_T();

  digitalWrite(4, LOW); // data bit
  wait_T();

  digitalWrite(4, LOW); // data bit
  wait_T();

  digitalWrite(4, LOW); // data bit
  wait_T();

  digitalWrite(4, LOW); // data bit
  wait_T();

  digitalWrite(4, HIGH); // data bit
  wait_T();

  digitalWrite(4, HIGH); // data bit
  wait_T();

  digitalWrite(4, LOW); // data bit
  wait_T();

  digitalWrite(4, HIGH); // parity bit
  wait_T();
  
  digitalWrite(4, HIGH); // stop bit
  delay(1000);
}

void wait_T() {
  for(int i = 0; i < 2186; i++)
    asm("NOP");
}
