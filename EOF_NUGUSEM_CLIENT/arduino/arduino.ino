#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

#define SDA_PIN 10
#define RST_PIN 9
#define SERVO_PIN 8
#define BUZZER_PIN 7
#define BUTTON_PIN 6


MFRC522 mfrc522(SDA_PIN, RST_PIN);
Servo myservo;

int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

void setup() {
  Serial.begin(9600);
  while (!Serial) { } // Serial 연결 대기

  SPI.begin();
  mfrc522.PCD_Init();
  myservo.attach(SERVO_PIN);
  myservo.write(0);
  pinMode(BUTTON_PIN, INPUT_PULLUP);//풀업저항 사용/ 평소:HIGH,버튼눌림:LOW
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  handleSerialCommands();
  handleRFID();
  handleButton();
}

void handleSerialCommands() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'A') 
    {
      int angle = Serial.parseInt();
      myservo.write(angle);
      delay(4000);
      myservo.write(0);
    } 
    else if (command == 'Z') 
    {
      tone(BUZZER_PIN, 1000);
      delay(1000);
      noTone(BUZZER_PIN);
    }
  }
}

void handleRFID() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    sendUIDtoRaspberryPi();
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  }
}

void handleButton() {
  if (sensingBTN()==LOW) {
    sendBTNReqtoRaspberryPi();
  }
}

void sendUIDtoRaspberryPi() {
  Serial.print("U");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();
  delay(500);
}

void sendBTNReqtoRaspberryPi() {
  Serial.print("T");
  Serial.println();
  delay(500);
}

bool sensingBTN() {
  // 디바운싱 적용
  int curr_state = digitalRead(BUTTON_PIN);

  if (curr_state == LOW && lastButtonState==HIGH) {
    lastDebounceTime = millis();//현재 시간을 밀리초로 표현
    lastButtonState=LOW;
    return HIGH;
  }
  else if (curr_state == HIGH && lastButtonState==LOW) 
  { // 마지막으로 디바운싱이 적용된 후의 시간 경과가 설정된 debounceDelay보다 크다면
    lastButtonState=HIGH;
    return LOW;
  }
  return HIGH;
}