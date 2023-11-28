#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

#define SDA_PIN 10
#define RST_PIN 9
#define SERVO_PIN 8
#define BUZZER_PIN 7
#define BUTTON_PIN 6

#define BUTTON_RELEASE HIGH
#define BUTTON_RELEASE HIGH


MFRC522 mfrc522(SDA_PIN, RST_PIN);
Servo myservo;

int buttonState = HIGH;
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
  pinMode(BUTTON_PIN, INPUT_PULLUP);
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
    if (command == 'A') {
      int angle = Serial.parseInt();
      myservo.write(angle);
      if (angle == 180) {
        delay(4000);
        myservo.write(0);
      }
    } else if (command == 'Z') {
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
  if (sensingBTN()) {
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
  //디바운싱은 나중에
  int reading = digitalRead(BUTTON_PIN);

  if (reading == LOW) {
    //lastDebounceTime = millis();
    Serial.println("asdfasdf");
    return true;
  }
  return false;

  /*
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) { // 제대로된 버튼입력
    if (reading != buttonState) {
      buttonState = reading;
      lastButtonState = reading;
      return true;
    }
  }
  else
  {
    return false;
  }
*/
}
