#include <Arduino.h>
#include <WiFi.h>

constexpr char TEST_SSID[] = "RoboZakBench-9B62";
constexpr uint16_t TEST_PORT = 38473;
constexpr size_t KEY_LENGTH = 16;
constexpr uint32_t AP_DURATION_MS = 120000;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(2000);
  WiFi.persistent(false);
}

void loop() {
  if (Serial.available() < KEY_LENGTH) {
    delay(10);
    return;
  }

  char key[KEY_LENGTH + 1] = {};
  if (Serial.readBytes(key, KEY_LENGTH) != KEY_LENGTH) {
    return;
  }
  const IPAddress address(192, 168, 47, 1);
  const IPAddress mask(255, 255, 255, 0);
  const bool started = WiFi.mode(WIFI_AP) && WiFi.softAPConfig(address, address, mask) &&
                       WiFi.softAP(TEST_SSID, key, 6, 0, 1);
  memset(key, 0, sizeof(key));
  if (!started) {
    Serial.println("AP_FAILED");
    WiFi.mode(WIFI_OFF);
    return;
  }

  NetworkServer server(TEST_PORT);
  server.begin();
  Serial.println("AP_READY");
  const uint32_t start = millis();
  while (millis() - start < AP_DURATION_MS) {
    NetworkClient client = server.accept();
    if (!client) {
      delay(10);
      continue;
    }
    client.setTimeout(1000);
    while (client.connected() && millis() - start < AP_DURATION_MS) {
      if (client.available()) {
        const String line = client.readStringUntil('\n');
        if (line.startsWith("PING ") && line.length() <= 9) {
          client.print("PONG ");
          client.println(line.substring(5));
        } else {
          client.println("ERR");
        }
      }
      delay(1);
    }
    client.stop();
  }
  server.end();
  WiFi.mode(WIFI_OFF);
}
