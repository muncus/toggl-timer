/*
 * Tag Tracker
 * print out the tag number of an rfid, and how long it has been present on the reader.
 * The ID of the tag is recorded when a new tag is read. as long as that tag
 * continues to be present, output nothing. when the card is removed, print the
 * ID, and the number of seconds it has been there, followed by a newline.
 */
 
 void setup(){
   Serial.begin(9600);
   Serial.println("starting up");
 }
 
 void loop(){
 }
