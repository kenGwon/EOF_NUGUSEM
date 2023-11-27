#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>


#define SDA_PIN 10
#define RST_PIN 9
#define SERVO_PIN 8
#define BUZZER_PIN 7
#define BUTTON_PIN 6
MFRC522 mfrc522(SDA_PIN, RST_PIN);
Servo myservo;  // 서보 모터 객체 생성

void sendOutReqtoRaspberryPi();
void sendUIDtoRaspberryPi();


int buttonState = HIGH;    // 현재 버튼 상태
int lastButtonState = HIGH;  // 이전 버튼 상태
unsigned long lastDebounceTime = 0;  // 마지막 디바운싱 타임아웃
unsigned long debounceDelay = 50;    // 디바운싱 지연 시간
int pos = 0;     // 서보 모터의 현재 위치



void setup() {
  Serial.begin(9600);
  while (!Serial);// serial 연결 될때까지 대기
  SPI.begin();
  mfrc522.PCD_Init();
  myservo.attach(SERVO_PIN);  // 서보 모터를 9번 핀에 연결
  myservo.write(0);
  pinMode(BUTTON_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);//모드 설정
}

void loop() {//무한루프

  if (Serial.available() > 0) {//rasp-serial listen
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
    if (command == 'Z') {
        tone(BUZZER_PIN, 1000);  // 피에조 부저를 500Hz로 울림
        delay(1000);  // 부저가 울릴 동안 잠시 대기
        noTone(BUZZER_PIN);  // 피에조 부저를 멈춤
    }
    if (command == 'T') {
      // 버튼 디바운싱 처리
      int reading = digitalRead(BUTTON_PIN);
      
      if (reading != lastButtonState) {
        lastDebounceTime = millis();
      }

      if ((millis() - lastDebounceTime) > debounceDelay) {
        if (reading != buttonState) {
          buttonState = reading;
          if (buttonState == LOW) {
            // 버튼이 눌렸을 때의 동작
            sendOutReqtoRaspberryPi();
          }
        }
      }
      lastButtonState = reading;
    }

  }

  // RFID 모듈에서 카드 감지
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {//rfid-gpio listen
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

void sendOutReqtoRaspberryPi() {
  Serial.print("M");  // 헤더 "M"를 붙여서 전송
  Serial.println();
  delay(1000); // 중복 전송 방지를 위한 딜레이
}
