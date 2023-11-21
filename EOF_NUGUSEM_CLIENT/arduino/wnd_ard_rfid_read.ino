#include <SPI.h>
#include <MFRC522.h>

#define SDA_PIN 10
#define RST_PIN 9

MFRC522 mfrc522(SDA_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  while (!Serial);
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("RFID-RC522 및 라즈베리파이 통신 예제");
}

void loop() {
  // RFID 모듈에서 카드 감지
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    Serial.print("카드 UID: ");
    printCardUID();

    // RFID UID를 라즈베리파이로 전송
    sendUIDtoRaspberryPi();

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  }
}

void printCardUID() {
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      Serial.print("0");
    }
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();
}

void sendUIDtoRaspberryPi() {
  Serial.print("U");  // 헤더 "U"를 붙여서 전송
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      Serial.print("0");
    }
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();
  delay(1000); // 중복 전송 방지를 위한 딜레이
}
