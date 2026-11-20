#include <Arduino.h>
#include <WiFi.h>

constexpr uint16_t TEST_PORT = 38473;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(3000);
  WiFi.persistent(false);
}

void loop() {
  if (Serial.available() < 2) {
    delay(10);
    return;
  }

  const int ssidLength = Serial.read();
  const int passwordLength = Serial.read();
  char ssid[33] = {};
  char password[65] = {};
  if (ssidLength < 1 || ssidLength > 32 || passwordLength < 8 || passwordLength > 64) {
    Serial.println("INVALID_INPUT");
    return;
  }
  if (Serial.readBytes(ssid, ssidLength) != ssidLength ||
      Serial.readBytes(password, passwordLength) != passwordLength) {
    Serial.println("INVALID_INPUT");
    return;
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  memset(password, 0, sizeof(password));
  const uint32_t started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 25000) {
    delay(100);
  }

  if (WiFi.status() != WL_CONNECTED || WiFi.localIP() == IPAddress(0, 0, 0, 0)) {
    Serial.println("CONNECT_FAILED");
    WiFi.mode(WIFI_OFF);
    return;
  }

  NetworkServer server(TEST_PORT);
  server.begin();
  Serial.print("READY ");
  Serial.println(WiFi.localIP());

  NetworkClient gateway;
  const bool gatewayReached = gateway.connect(WiFi.gatewayIP(), 80, 2500) ||
                              gateway.connect(WiFi.gatewayIP(), 443, 2500);
  gateway.stop();
  Serial.println(gatewayReached ? "GATEWAY_TCP_OK" : "GATEWAY_TCP_NO_REPLY");

  const uint32_t listenStarted = millis();
  while (millis() - listenStarted < 15000) {
    NetworkClient client = server.accept();
    if (client) {
      client.setTimeout(1000);
      if (client.readStringUntil('\n') == "ROBOZAK_LAN_PING") {
        client.print("ROBOZAK_LAN_PONG\n");
        client.stop();
        break;
      }
      client.stop();
    }
    delay(10);
  }

  server.end();
  WiFi.mode(WIFI_OFF);
}
