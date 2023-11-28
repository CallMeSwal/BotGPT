 /* Include the HCPCA9685 library */
#include "HCPCA9685.h"

/* I2C slave address for the device/module. For the HCMODU0097 the default I2C address
   is 0x40 */
#define  I2CAdd 0x43


/* Create an instance of the library */
HCPCA9685 HCPCA9685(I2CAdd);

//sway commands, h: happy, s: sad, n: neutral, b: blink
//char cmd = 's';
String coor = "";
int currX = 150;
int currY = 300;
int targetX=currX;
int targetY=currY;


//ctrl
int pos_sway = 50;
int dir_sway = 1;
int pos_pitch = 250;
int dir_pitch = 1;
int lim_pitch=450;
int start_pitch = 300;

//motor index
int lidLeftTop = 0;
int lidLeftBot = 1;
int lidRightTop = 2;
int lidRightBot = 3;
int motorSway = 4;
int motorPitch = 5;

//timer
unsigned long currentMillis;
long previousMillis = 0;    // set up timers
long lastBlinkMillis = 0;    // set up timers
long interval = 10;        // time constant for timer
long blinkDelay = 10000;

void setup() 
{
  Serial.setTimeout(2); //Milliseconds
  /* Initialise the library and set it to 'servo mode' */ 
  HCPCA9685.Init(SERVO_MODE);

  /* Wake the device up */
  HCPCA9685.Sleep(false);
  Serial.begin(115200);

  // Middle the eyes
  HCPCA9685.Servo(motorSway, currX); // sway (middle)
  HCPCA9685.Servo(motorPitch, currY); // pitch (middle)

  //left side eyelids
  HCPCA9685.Servo(0, 430); //left top eyelid (open)
  HCPCA9685.Servo(1, 0); //left bottom eyelid (open)

  //right side eyelids
  HCPCA9685.Servo(2, 0); //right top eyelid (open)
  HCPCA9685.Servo(3, 430); //right bottom eyelid (open)
  
  delay(500);
}


void loop(){
  //HCPCA9685.Servo(motorSway, targetX); // sway
  //HCPCA9685.Servo(motorPitch, targetY); // pitch
  currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {  // start 5ms timed loop  
    if(currX != targetX){
      currX = currX + int(round((targetX-currX)*0.5));
      HCPCA9685.Servo(motorSway, targetX); // sway
      currX=targetX;
      }
    if(currY != targetY){
      currY = currY + int(round((targetY-currY)*0.5));
      HCPCA9685.Servo(motorPitch, targetY); // pitch
      currY=targetY;
      }
    if(currentMillis - lastBlinkMillis > blinkDelay){
      if(blinkDelay%2==1){
        //left side eyelids
        HCPCA9685.Servo(0, 350); //left top eyelid (close)
        HCPCA9685.Servo(1, 80); //left bottom eyelid (close)
        delay(25);
        //right side eyelids
        HCPCA9685.Servo(2, 80); //right top eyelid (close)
        HCPCA9685.Servo(3, 350); //right bottom eyelid (close)
        delay(150);
        HCPCA9685.Servo(0, 430); //left top eyelid (open)
        HCPCA9685.Servo(1, 0); //left bottom eyelid (open)
        delay(25);
        //right side eyelids
        HCPCA9685.Servo(2, 0); //right top eyelid (open)
        HCPCA9685.Servo(3, 430); //right bottom eyelid (open)
        delay(150);
        }
      else{
        //left side eyelids
        HCPCA9685.Servo(0, 350); //left top eyelid (close)
        HCPCA9685.Servo(1, 80); //left bottom eyelid (close)
        delay(25);
        //right side eyelids
        HCPCA9685.Servo(2, 80); //right top eyelid (close)
        HCPCA9685.Servo(3, 350); //right bottom eyelid (close)
        delay(150);
        HCPCA9685.Servo(0, 430); //left top eyelid (open)
        HCPCA9685.Servo(1, 0); //left bottom eyelid (open)
        delay(25);
        //right side eyelids
        HCPCA9685.Servo(2, 0); //right top eyelid (open)
        HCPCA9685.Servo(3, 430); //right bottom eyelid (open)
        delay(150);
        //left side eyelids
        HCPCA9685.Servo(0, 350); //left top eyelid (close)
        HCPCA9685.Servo(1, 80); //left bottom eyelid (close)
        delay(25);
        //right side eyelids
        HCPCA9685.Servo(2, 80); //right top eyelid (close)
        HCPCA9685.Servo(3, 350); //right bottom eyelid (close)
        delay(150);
        HCPCA9685.Servo(0, 430); //left top eyelid (open)
        HCPCA9685.Servo(1, 0); //left bottom eyelid (open)
        delay(25);
        //right side eyelids
        HCPCA9685.Servo(2, 0); //right top eyelid (open)
        HCPCA9685.Servo(3, 430); //right bottom eyelid (open)
        delay(150);  
        }
      blinkDelay = random(8000, 20000);
      lastBlinkMillis = currentMillis;
      }
    previousMillis = currentMillis;
    } // end of timed loop
  //delay(1000);
  recCommand();
}
  
void recCommand() {
  if (Serial.available() > 0) {
      //targetX = 50;
      //targetY = 200;
      coor = Serial.readStringUntil("-");
      coor = coor.substring(0, coor.indexOf("-"));
      int coor_x = coor.substring(0, coor.indexOf(",")).toInt();
      int coor_y = coor.substring(coor.indexOf(",")+1).toInt();
      targetX = map(coor_x, 0, 640, 50, 250);
      targetY = map(coor_y, 0, 480, 175, 425);
      //Serial.print(targetX);
      //Serial.print(" ");
      //Serial.println(targetY);    
      Serial.flush();
  }
}
