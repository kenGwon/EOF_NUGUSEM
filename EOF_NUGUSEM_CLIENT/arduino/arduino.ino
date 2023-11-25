#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>


#define SDA_PIN 10
#define RST_PIN 9
#define SERVO_PIN 8
MFRC522 mfrc522(SDA_PIN, RST_PIN);
Servo myservo;  // 서보 모터 객체 생성

void sendUIDtoRaspberryPi();



int pos = 0;     // 서보 모터의 현재 위치
void setup() {
  Serial.begin(9600);
  while (!Serial);// serial 연결 될때까지 대기
  SPI.begin();
  mfrc522.PCD_Init();
  myservo.attach(SERVO_PIN);  // 서보 모터를 9번 핀에 연결
  myservo.write(0);
}

void loop() {//무한루프

  if (Serial.available() > 0) {
    char command = Serial.read();
    
    if (command == 'A') {
      // 각도 정보 읽기
      int angle = Serial.parseInt();
      // 서보 모터 위치 설정
      myservo.write(angle);
      if(angle==180)//열렸다면 
      {
        delay(4000);//4초간 열린상태 유지 후 
        myservo.write(0);//닫기
      }
    }

  }

/*SERVO MOTOR
  for (pos = 0; pos <= 180; pos += 1) {  // 0도에서 180도까지 회전
    myservo.write(pos);                  // 서보 모터 위치 설정
    //delay(15);                           // 15ms 딜레이
  }
  delay(1000);                           // 1초 딜레이

  for (pos = 180; pos >= 0; pos -= 1) {  // 180도에서 0도까지 회전
    myservo.write(pos);                  // 서보 모터 위치 설정
    //delay(15);                           // 15ms 딜레이
  }
  delay(5000);    
*/


  // RFID 모듈에서 카드 감지
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    //Serial.print("카드 UID: ");//디버그용
    //printCardUID();//디버그용

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
