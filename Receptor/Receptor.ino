#include <SPI.h>
#include <LoRa.h>

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("LoRa Receiver");

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // received a packet
    String receivedData = "";

    // read packet
    while (LoRa.available()) {
      receivedData += (char)LoRa.read();
    }

    // send received data to serial
    Serial.println(receivedData);
  }
    delay(10);
}