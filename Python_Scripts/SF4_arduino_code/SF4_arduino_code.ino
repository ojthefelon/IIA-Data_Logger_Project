#include <SPI.h>

SPISettings settings(2000000, MSBFIRST, SPI_MODE0);

const int CS = 10;
const int CH1_att = 5;
const int CH1_coup = 4;
const int CH2_att = 2;
const int CH2_coup = 3;

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

const uint8_t SYNC1 = 0xAB;
const uint8_t SYNC2 = 0x57;
uint8_t pkt[6] = {SYNC1, 0, 0, 0, 0, SYNC2};
uint8_t cmd;

void setup() {
  Serial.begin(1000000);
  pinMode(CS, OUTPUT);
  pinMode(CH1_att, OUTPUT);
  pinMode(CH1_coup, OUTPUT);
  pinMode(CH2_att, OUTPUT);
  pinMode(CH2_coup, OUTPUT);
  digitalWrite(CS, HIGH);
  digitalWrite(CH1_att, HIGH);
  digitalWrite(CH1_coup,LOW); //Low = AC coupling
  digitalWrite(CH2_att,HIGH);
  digitalWrite(CH2_coup,LOW);
  SPI.begin();
}

void loop() {
  //assign coupling and attenuation settings
  if (Serial.available()) {
    //instructions received from the pc in the form of one byte: {0, 0, 0, 0, CH2_coup, CH2_att, CH1_coup, CH1_att}
    cmd = Serial.read();
    digitalWrite(CH1_att, (cmd >> 0) & 1);
    digitalWrite(CH1_coup, (cmd >> 1) & 1);
    digitalWrite(CH2_att, (cmd >> 2) & 1);
    digitalWrite(CH2_coup, (cmd >> 3) & 1);
    Serial.flush();
  }
  read_ADC();
  Serial.write(pkt,6);
}

void read_ADC() {
  SPI.beginTransaction(settings);

  //first channel
  digitalWrite(CS, LOW);
  SPI.transfer(read_1_CH0);
  pkt[1] = SPI.transfer(read_2);
  pkt[2] = SPI.transfer(read_3);
  digitalWrite(CS,HIGH);

  //second channel
  digitalWrite(CS,LOW);
  SPI.transfer(read_1_CH1);
  pkt[3] = SPI.transfer(read_2);
  pkt[4] = SPI.transfer(read_3);
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


