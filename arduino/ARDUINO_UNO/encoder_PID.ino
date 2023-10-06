#include "SoftwareSerial.h"

#define dir_1 6
#define pwm_left 4
#include <avr/sleep.h>

#define dir_2 7
#define pwm_right 5


//const int pingPin = 9; // Trigger Pin of Ultrasonic Sensor
//const int echoPin = 10; // Echo Pin of Ultrasonic Sensor

String DEVICE_ID="INFY5GAGV1";
String device_id; // Variable to store the device ID
String duration_received;
String speed_received;

String direction_command;
int duration  = 0;       // Variable to store the duration

int  speed  = 50 ;// MAX 255

long int start_time = 0;
volatile long leftEncoderCount = 0;  // Volatile because these variables are modified in an interrupt context
volatile long rightEncoderCount = 0;

float Kp =1.5;// Proportional constant
float Ki =0.08;// Integral constant
float Kd =0.45; // Derivative constant

//long targetCount = 1000; // Example target count
float prevError = 0;
float integral = 0;
bool movementCommandReceived = false;
unsigned long commandReceivedTime = 0;

void setup() {
  // Configure pins as outputs
  pinMode(pwm_left, OUTPUT);
  pinMode(dir_1, OUTPUT);
  pinMode(pwm_right, OUTPUT);
  pinMode(dir_2, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(18), leftEncoderInterrupt, CHANGE);
  attachInterrupt(digitalPinToInterrupt(20), rightEncoderInterrupt, CHANGE);
  // Start serial communication
  Serial.begin(9600);
}
void leftEncoderInterrupt() {
  if (digitalRead(18) == digitalRead(19)) {
    leftEncoderCount++;
  } else {
    leftEncoderCount--;
  }
}

void rightEncoderInterrupt() {
  if (digitalRead(20) == digitalRead(21)) {
    rightEncoderCount++;
  } else {
    rightEncoderCount--;
  }
}
void loop() {
 

   
   
   
   
  if(duration != 0 && (millis()-start_time) >= duration){
    start_time =0;
    duration = 0;
    STOP();
  }
   
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove leading/trailing whitespaces
    Serial.print("recieved = ");
    Serial.println(command);

    // Split the message into parts
    int delimiterIndex1 = command.indexOf('_');
    int delimiterIndex2 = command.indexOf('_', delimiterIndex1 + 1);
    int delimiterIndex3 = command.indexOf('_', delimiterIndex2 + 1);

    if (delimiterIndex1 != -1 && delimiterIndex2 != -1) {
      device_id = command.substring(0, delimiterIndex1);                  // Extract Device_id
      direction_command = command.substring(delimiterIndex1 + 1, delimiterIndex2); // Extract Direction
      duration_received = command.substring(delimiterIndex2 + 1, delimiterIndex3);                  // Extract duration
      speed_received = command.substring(delimiterIndex3 + 1);
      duration=duration_received.toInt();
      speed=speed_received.toInt();
    }
   

    if (device_id == DEVICE_ID) {
      movementCommandReceived = true;
      commandReceivedTime = millis();

    leftEncoderCount=0;
     rightEncoderCount=0;
      if (direction_command == "FORWARD") {
        moveForward();
      } else if (direction_command == "BACKWARD") {
        moveBackward();
      } else if (direction_command == "RIGHT") {
         moveRight();
      } else if (direction_command == "LEFT") {
         moveLeft();
      } else if (direction_command == "STOP") {
         STOP();
      }
    }
  }
  if (movementCommandReceived) {
    unsigned long elapsedTime = millis() - commandReceivedTime;
//    if(direction_command == "FORWARD"){
//      Serial.print("F   |   ");
//      float Kp = 0.6;
//      float Ki = 0.02;
//      float Kd = 0.1;
//    } else if (direction_command == "LEFT") {
//        float Kp = 0.7;
//              Serial.print(Kp);
//        float Ki = 00.02;
//        float Kd= 0.15;
//    } else if (direction_command == "RIGHT") {
//        float Kp = 0;
//        float Ki = 0;
//        float Kd = 0;
//            
//    
//    }  
    // leftEncoderCount=0;
    // rightEncoderCount=0;
   if (elapsedTime < duration || duration == 0) {
    delay(100);
    noInterrupts(); // Disable interrupts while printing
    Serial.print("Left Encoder Count: ");
    Serial.println(leftEncoderCount);
    Serial.print("Right Encoder Count: ");
    Serial.println(rightEncoderCount);
    interrupts(); // Re-enable interrupts


   
    long leftCount = abs(leftEncoderCount);
    long rightCount = abs(rightEncoderCount);
    long error = leftCount - rightCount;
    Serial.println(error);
    // Calculate PID terms
    float P = Kp * error;
    integral += Ki * error;
    float D = Kd * (error - prevError);
   
    prevError = error;
   
    // Calculate motor speed adjustment
    float speedAdjustment = P + integral + D;
   
    // Calculate adjusted motor speeds
    int leftSpeed = speed - speedAdjustment;
    int rightSpeed = speed + speedAdjustment;
   
    // Limit adjusted speeds to the allowed range
    leftSpeed = constrain(leftSpeed, 0, 255);
    rightSpeed = constrain(rightSpeed, 0, 255);
    Serial.print("leftSpeed: ");
    Serial.println(leftSpeed);
    Serial.print("RighSpeed: ");
    Serial.println(rightSpeed);
    // Apply motor control
    analogWrite(pwm_left, leftSpeed);
    analogWrite(pwm_right, rightSpeed);
   
  }
  } else {
        STOP();
    movementCommandReceived = false; // Reset the flag
  }

}


void moveForward() {
  digitalWrite(dir_1, HIGH);
  digitalWrite(dir_2, HIGH);
  analogWrite(pwm_left, speed);
  analogWrite(pwm_right, speed);
  if(duration!=0){
    start_time = millis();
  }
  //movementCommandReceived = false;
}

void moveBackward() {
  digitalWrite(dir_1, LOW);
  digitalWrite(dir_2, LOW);
  analogWrite(pwm_left, speed);
  analogWrite(pwm_right, speed);
  if(duration!=0){
    start_time = millis();
  }
}

void moveLeft() {
  digitalWrite(dir_1, LOW);
  digitalWrite(dir_2, HIGH);
  analogWrite(pwm_left, speed);
  analogWrite(pwm_right, speed);
  if(duration!=0){
    start_time = millis();
  }
}

void moveRight() {
  digitalWrite(dir_1, HIGH);
  digitalWrite(dir_2, LOW);
  analogWrite(pwm_left, speed);
  analogWrite(pwm_right, speed);
  if(duration!=0){
   start_time = millis();
  }
}
void STOP() {
  digitalWrite(dir_1, HIGH);
  digitalWrite(dir_2, HIGH);
  analogWrite(pwm_left, 0);
  analogWrite(pwm_right, 0);
  movementCommandReceived = false;
}