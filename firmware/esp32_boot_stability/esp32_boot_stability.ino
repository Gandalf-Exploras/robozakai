#include <Arduino.h>

constexpr uint32_t HEARTBEAT_INTERVAL_MS = 1000;
uint32_t lastHeartbeatMs;
uint32_t heartbeatCount = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("ROBOZAK_BOOT");
  lastHeartbeatMs = millis();
}

void loop() {
  const uint32_t uptimeMs = millis();
  if (uptimeMs - lastHeartbeatMs >= HEARTBEAT_INTERVAL_MS) {
    lastHeartbeatMs = uptimeMs;
    Serial.print("HEARTBEAT seq=");
    Serial.print(++heartbeatCount);
    Serial.print(" uptime_ms=");
    Serial.println(uptimeMs);
  }
  delay(1);
}
