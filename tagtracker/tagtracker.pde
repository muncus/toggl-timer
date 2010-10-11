#include <AFSoftSerial.h>

/*
 * Tag Tracker
 * print out the tag number of an rfid, and how long it has been present on the reader.
 * The ID of the tag is recorded when a new tag is read. as long as that tag
 * continues to be present, output nothing. when the card is removed, print the
 * ID, and the number of seconds it has been there, followed by a newline.
 */
 
#define RFID_TAG_LENGTH 10  //bytes needed to read the tag id.
#define RFID_TAG_INPUT  10  //bytes of input required to read a whole tag.

#define PIN_RESET 7
#define PIN_RFID_TX 8 // not used.
#define PIN_RFID_RX 9

AFSoftSerial rfid = AFSoftSerial(PIN_RFID_RX, PIN_RFID_TX);
byte temptag[10];

void setup(){
  Serial.begin(9600);
  Serial.println("starting up");
  
  

  rfid.begin(9600);
}

void loop(){
  //Serial.println("waiting for data");
  //if(rfid.available() > 0){
    //we have some data. read it.
    Serial.println("reading data");
    readID12(temptag);
    // print it.
    Serial.println("printing data");
    for (int i=0; i<5; i++){
      //if (temptag[i] < 16) Serial.print("0");
      Serial.print(temptag[i], HEX);
    }
  //}
  Serial.println("waiting");
  delay(200);

}

/**
 * read data from rfid reader
 * @return rfid tag number
 *
 * Based on code by BARRAGAN, HC Gilje, djmatic, Martijn
 * http://www.arduino.cc/playground/Code/ID12 
 */
boolean readID12(byte *code)

{
  Serial.println("reading from id12");
  boolean result = false;
  byte val = 0;
  byte bytesIn = 0;
  byte tempbyte = 0;
  byte checksum = 0;

  // read 10 digit code + 2 digit checksum
  while (bytesIn < RFID_TAG_INPUT)
  {
    //Serial.println("about to read a byte..");
    
    
    if( rfid.available() > 0) 
    //if( 1)
    { 
      Serial.println("reading a byte..");
      val = rfid.read();
      
      Serial.print("read: ");
      Serial.println(val, BYTE)
      
      ;

      // if CR, LF, ETX or STX before the 10 digit reading -> stop reading
      if((val == 0x0D)||(val == 0x0A)||(val == 0x03)||(val == 0x02)) break;

      // Do Ascii/Hex conversion:
      if ((val >= '0') && (val <= '9')) 
        val = val - '0';
      else if ((val >= 'A') && (val <= 'F'))
        val = 10 + val - 'A';


      // Every two hex-digits, add byte to code:
      if (bytesIn & 1 == 1) 
      {
        // make some space for this hex-digit by
        // shifting the previous hex-digit with 4 bits to the left:
        code[bytesIn >> 1] = (val | (tempbyte << 4));

        // If we're at the checksum byte, Calculate the checksum... (XOR)
        if (bytesIn >> 1 != RFID_TAG_LENGTH) checksum ^= code[bytesIn >> 1]; 
      } 
      else 
      {
        // Store the first hex digit first...
        tempbyte = val;                           
      }

      // ready to read next digit
      bytesIn++;                                
    } 
  }

  // read complete
  if (bytesIn == RFID_TAG_INPUT) 
  { 
    // valid tag
    if(code[5] == checksum) result = true; 
  }

  // reset id-12
  //updateID12(true);


  return result;
}


