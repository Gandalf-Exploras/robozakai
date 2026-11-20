#include <Arduino.h>

constexpr uint32_t HEARTBEAT_INTERVAL_MS = 1000;
constexpr size_t MAX_COMMAND_LENGTH = 32;
uint32_t lastHeartbeatMs;
uint32_t heartbeatCount = 0;
char command[MAX_COMMAND_LENGTH];
size_t commandLength = 0;
bool commandTooLong = false;

void respondToCommand() {
  if (commandLength > 0 && command[commandLength - 1] == '\r') {
    --commandLength;
  }

  constexpr char PREFIX[] = "PING ";
  constexpr size_t PREFIX_LENGTH = sizeof(PREFIX) - 1;
  if (commandTooLong || commandLength <= PREFIX_LENGTH ||
      memcmp(command, PREFIX, PREFIX_LENGTH) != 0) {
    Serial.println("ERR");
    return;
  }

  for (size_t index = PREFIX_LENGTH; index < commandLength; ++index) {
    if (command[index] < '0' || command[index] > '9') {
      Serial.println("ERR");
      return;
    }
  }
  Serial.print("PONG ");
  Serial.write(reinterpret_cast<const uint8_t*>(command + PREFIX_LENGTH),
               commandLength - PREFIX_LENGTH);
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  Serial.println("ROBOZAK_BOOT");
  lastHeartbeatMs = millis();
}

void loop() {
  while (Serial.available() > 0) {
    const int input = Serial.read();
    if (input == '\n') {
      respondToCommand();
      commandLength = 0;
      commandTooLong = false;
    } else if (commandLength < MAX_COMMAND_LENGTH) {
      command[commandLength++] = static_cast<char>(input);
    } else {
      commandTooLong = true;
    }
  }

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
