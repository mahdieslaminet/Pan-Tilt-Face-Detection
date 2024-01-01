#include <Servo.h>

Servo panServo;   // Define servo for pan movement
Servo tiltServo;  // Define servo for tilt movement

const int panPin = 9;    // Connect pan servo to pin 9
const int tiltPin = 10;  // Connect tilt servo to pin 10

//face detection (4.5)
//color detection(3)
int ds = 4.5;

void setup() {
  Serial.begin(9600);    // Start serial communication
  panServo.attach(panPin);
  tiltServo.attach(tiltPin);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();

    switch (command) {
      case 'u':
        tiltServo.write(tiltServo.read() - ds);  // Incrementally move tilt up
        //delay(5);
        break;
      case 'd':
        tiltServo.write(tiltServo.read() + ds);  // Incrementally move tilt down
        //delay(5);
        break;
      case 'l':
        panServo.write(panServo.read() - ds);    // Incrementally move pan left
        //delay(5);
        break;
      case 'r':
        panServo.write(panServo.read() + ds);    // Incrementally move pan right
        //delay(5);
        break;
      case 's':
        panServo.write(90);   // Stop pan (set to center position)
        tiltServo.write(90);  // Stop tilt (set to center position)
        break;
      default:
        break;
    }
  }
}