#include <SPI.h>

SPISettings settings(2000000, MSBFIRST, SPI_MODE0);

const int CS = 10;
const int CH1_att = 5;
const int CH1_coup = 4;

//Configuration:
//Byte 1: 0 0 0 0 1 SGL/DIFF D2 D1
//Byte 2: D0 X X X X X X X
//Byte 3: X X X X X X X X
//For Channel 0 read: D2 D1 D0 = 000
//For Channel 1 read: D2 D1 D0 = 010
uint8_t read_1_CH0 = 0b00001000;
uint8_t read_1_CH1 = 0b00001001;
uint8_t read_2 = 0b00000000;
uint8_t read_3 = 0b00000000;

const uint8_t SYNC = 0xAB;
uint8_t pkt[5] = {SYNC, 0, 0, 0, 0};

float reading_1;
float reading_2;

void setup() {
  Serial.begin(115200,SERIAL_8N1);//change back to 1Mb later
  SPI.begin();
}

void loop() {
  read_ADC();
  Serial.write(pkt,5);
  /*
  int16_t reading = (int16_t)pkt[1]<<8 | (int16_t)pkt[2];
  Serial.println(reading);
  reading = (int16_t)pkt[3]<<8 | (int16_t)pkt[4];
  Serial.println(reading);
  //delay(10);*/
}

void read_ADC() {
  SPI.beginTransaction(settings);
  digitalWrite(CS, LOW);

  SPI.transfer(read_1_CH0);
  pkt[1] = SPI.transfer(read_2);
  pkt[2] = SPI.transfer(read_3);
  // pkt[1] = 0x02;
  // pkt[2] = 0xAC; //(684)

  digitalWrite(CS,HIGH);
  //second channel
  digitalWrite(CS,LOW);

  SPI.transfer(read_1_CH1);
  pkt[3] = SPI.transfer(read_2);
  pkt[4] = SPI.transfer(read_3);
  // pkt[3] = 0x37;
  // pkt[4] = 0x06;//reminder, we are using signed inputs, 12 bits of the value and 13 bits of sign, acocunt for this in python code (-2298)

  digitalWrite(CS,HIGH);

  SPI.endTransaction();

  //from first byte: removing garbage first 3 bits and sign extending
  pkt[1]=pkt[1]&0x1F;
  if (pkt[1]&0x10) {
    pkt[1] = pkt[1] | 0xE0;
  }
  pkt[3]=pkt[3]&0x1F;
  if (pkt[3]&0x10) {
    pkt[3] = pkt[3] | 0xE0;
  }
}