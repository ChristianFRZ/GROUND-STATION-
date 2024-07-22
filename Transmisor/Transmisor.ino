#include <SoftwareSerial.h>
#include <TinyGPS.h>
#include <LoRa.h>

TinyGPS gps;
SoftwareSerial ss(4, 3); // RX, TX

// Pines
#define SS 10
#define RST 9
#define DIO0 2

void setup() {
  Serial.begin(9600);

  ss.begin(9600);

  LoRa.setPins(SS, RST, DIO0);
  if (!LoRa.begin(433E6)) { // frecuencia
    Serial.println("Error al inicializar LoRa");
    while (1);
  }
  Serial.println("LoRa inicializado correctamente");
}

void loop() {
  while (ss.available()) {
    char c = ss.read();
    if (gps.encode(c)) {
      float flat, flon, falt;
      unsigned long age;
      gps.f_get_position(&flat, &flon, &age);
      falt = gps.f_altitude(); 

      int year;
      byte month, day, hour, minute, second, hundredths;
      gps.crack_datetime(&year, &month, &day, &hour, &minute, &second, &hundredths, &age);

      if (age != TinyGPS::GPS_INVALID_AGE) {
        String message = "Lat: " + String(flat, 6) + ", Lon: " + String(flon, 6) + 
                         ", Alt: " + String(falt, 2) + "m" +
                         ", Date: " + String(year) + "/" + String(month) + "/" + String(day);

        LoRa.beginPacket();
        LoRa.print(message);
        LoRa.endPacket();

        Serial.println(message);
      }
    }
  }
}
