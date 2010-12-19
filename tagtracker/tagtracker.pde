/*
 * Tag Tracker
 * print out the tag number of an rfid, and how long it has been present on the reader.
 * The ID of the tag is recorded when a new tag is read. as long as that tag
 * continues to be present, output nothing. when the card is removed, print the
 * ID, and the number of seconds it has been there, followed by a newline.
 */
#include <NewSoftSerial.h>

#define DEBUG 1

#define RFID_TAG_LENGTH 10  //bytes needed to read the tag id.
#define RFID_TAG_INPUT  16  //bytes of input required to read a whole tag.

#define PIN_RESET 7
#define PIN_RFID_TX 8 // not used.
#define PIN_RFID_RX 9
#define PIN_CLOCK_RUNNING 13 //indicates that we are clocked in

NewSoftSerial rfid = NewSoftSerial(PIN_RFID_RX, PIN_RFID_TX);
char temptag[RFID_TAG_LENGTH];
char currentTag[RFID_TAG_LENGTH+1]; // the tag we are currently tracking.
unsigned long tagStartTime = 0;      // time at which we first saw currentTag
boolean tagPresent = false;

void setup(){
  pinMode(PIN_RESET, OUTPUT); // set our reset pin up for resetting.
  digitalWrite(PIN_RESET, HIGH);

  pinMode(PIN_CLOCK_RUNNING, OUTPUT);
  digitalWrite(PIN_CLOCK_RUNNING, LOW);
  
  memset(currentTag, 0, 11);
  memset(temptag, 0, 10);

  Serial.begin(9600);
  Serial.println("# starting up");

  rfid.begin(9600);
  
}

void loop(){
  //Serial.println("# reading data");
  tagPresent = readRaw(temptag);
  
  if(tagPresent && tagStartTime == 0){
    //we dont have a tag, record it.
    Serial.print("# clocking in: ");
    Serial.println(temptag);

    strncpy(currentTag, temptag, 10);
    tagStartTime = millis();
    Serial.println("# got a new tag");
    digitalWrite(PIN_CLOCK_RUNNING, HIGH);
  }
  else if ( tagPresent && tagStartTime != 0 ){
    if(tagsEqual(temptag, currentTag) == 0){
        Serial.println("# read current tag again, clocking out.");

        Serial.print(currentTag);
        Serial.print(" ");
        Serial.println((millis() - tagStartTime)/1000); //seconds since tag seen.
        memset(currentTag, 0, 11);
        tagStartTime = 0;
        digitalWrite(PIN_CLOCK_RUNNING, LOW);
    }
    else {
      Serial.println("# tags didnt match. :(");
    }
  }

  resetRfid();
  delay(200);

}

void resetRfid(){
  //durp.
  digitalWrite(PIN_RESET, LOW);
  delay(1000);
  digitalWrite(PIN_RESET, HIGH);
}

//just grab the bytes, and return them.
boolean readRaw(char *code)
{
  //Serial.println("reading from id12");
  boolean result = false;
  char a_val = 0; //ascii value we read.
  int  i_val = 0; //int value which corresponds to a_val
  char expected_checksum[2] = {
    0,0  };
  char calculated_checksum[2] = {
    0,0  };

  // read 10 digit code + 2 digit checksum

  if( rfid.available() > 0)
  { 

    a_val = rfid.read();

    //Serial.println(val, BYTE);
    // 0x0D == CR
    // 0x0A == LF
    // 0x03 == ETX

    if(a_val == 0x02){
      Serial.println("# found STX");
    } 
    else {
      Serial.println("# invalid read.");
      return false;
    }

    for(int i=0;i<RFID_TAG_LENGTH;i++){
      int ci = 0; //checksum index.
      code[i] = rfid.read();
      i_val = ctoi(code[i]);
      
      if(DEBUG){
        Serial.print("# read: ");
        Serial.println(code[i], HEX);
      }
      if(i<5){
        ci = 0;
      } 
      else {
        ci = 1;
      }
      calculated_checksum[ci] ^= i_val;
      //Serial.print("CS: ");
      //Serial.println(calculated_checksum, HEX);
    }

    //chomp the end off.
    //checksum
    //TODO: make checksumming actually work.
    //a_val = rfid.read();
    expected_checksum[0] = ctoi(rfid.read());
    
    //a_val = rfid.read();
    expected_checksum[1] = ctoi(rfid.read());

    /** WTF. checksumming doesnt work the way i expect it to, apparently.
    for(int i=0;i<2;i++){
      if(expected_checksum[i] == calculated_checksum[i]){
        Serial.println("checksum matched");
        Serial.print(calculated_checksum[i], HEX);
      } 
      else {
        Serial.print("checksum: ");
        Serial.print(calculated_checksum[i], HEX);
        Serial.print(" vs ");
        Serial.println(expected_checksum[i], HEX);
      }
    }
    */
    
    //TODO: put some assertions in here for error checking.
    //cr/lf
    //Serial.println(rfid.read(), HEX);
    //Serial.println(rfid.read(), HEX);
    rfid.read();
    rfid.read();
    //etx
    rfid.read();
    //Serial.println(rfid.read(), HEX);
    return true;

  } 
  //no serial data.
  return false;
}

int ctoi(char c){
  if('0' <= c && c <= '9')
    return int(c - '0');
  if('A' <= c && c <= 'F')
    return int(10 + c - 'A');
  return 0; //catchall.
}

boolean tagsEqual(char* t1, char* t2){
  return (strncmp(t1, t2, 10));
}


