#include<Servo.h>

Servo n ;
char m;
long int k;
void setup() {
  n.attach(5);
  Serial.begin(9600);
  n.write(90);
}

void loop() {
if(Serial.available()>2){
  m =Serial.read();
  k =Serial.parseInt();
 if(m =='a'){
    n.write(k);  
  }
  delay(10);
  }
  
}