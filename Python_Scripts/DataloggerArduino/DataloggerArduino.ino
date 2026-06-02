#include <Arduino.h> 

unsigned long last_transmission = 0;
unsigned long transmission_interval = 20;
byte incoming_command = 0;

void setup() {
  Serial.begin(115200);

}
// send a sin wave over serial for testing
void loop() {
  unsigned long now = millis();
  if (now - last_transmission > transmission_interval){
    last_transmission=now;
    Serial.println(sin(now*M_PI/500));
  }



}
