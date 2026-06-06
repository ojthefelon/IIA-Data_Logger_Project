#include <Arduino.h> 

unsigned long last_transmission = 0;
unsigned long transmission_interval = 20;
int num_channels = 2;
byte read;
bool Began = False;
bool Coupling = {True}*num_channels;//True represents DC coupling
bool Attnuation = {True}*num_channels;//True represents 1x attenuation


void setup() {
  Serial.begin(115200);
}


void loop() {
  if (Serial.available()){
    read = Serial.read()
  }
  // send a sin wave over serial for testing
  unsigned long now = millis();
  if (now - last_transmission > transmission_interval){
    last_transmission=now;
    Serial.println(sin(now*M_PI/500)+0.2*sin(now*M_PI/50));
  }
}
