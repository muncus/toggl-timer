/*
 * Time tracking for TV and Video Games.
 */
#include <SoftwareSerial.h>

#define DEBUG 0

#define PIN_BUTTON_TV 3
#define PIN_BUTTON_VG 4

#define PIN_CLOCK_RUNNING 13 //indicates that we are clocked in

unsigned long tagStartTime = 0;      // time at which we first saw currentTag
boolean tagPresent = false;

int lastButtonState;

void setup(){
  pinMode(PIN_BUTTON_TV, INPUT);
  pinMode(PIN_BUTTON_VG, INPUT);

  pinMode(PIN_CLOCK_RUNNING, OUTPUT);
  digitalWrite(PIN_CLOCK_RUNNING, LOW);
  
  lastButtonState = digitalRead(PIN_BUTTON_TV);
  
  Serial.begin(9600);
  Serial.println("# starting up");

}

void loop(){
  
  int buttonState = digitalRead(PIN_BUTTON_TV);
  
  if( buttonState == HIGH ){
    if( ! tagPresent ){
      Serial.println("# first press, recorded.");
      tagStartTime = millis();
      digitalWrite(PIN_CLOCK_RUNNING, HIGH);
      tagPresent = true;
      delay(200); //deter bouncing.
    }
    else {
      //second push, do the math, and emit the data.
      int duration = (millis() - tagStartTime)/1000; //seconds.
      Serial.print(duration);
      Serial.print(" ");
      Serial.print("Watching TV");
      Serial.println("");
      //reset stored state.
      digitalWrite(PIN_CLOCK_RUNNING, LOW);
      tagStartTime = 0;
      tagPresent = false;
      delay(200); //deter bouncing.

    }
  }
}

