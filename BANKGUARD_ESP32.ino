#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include "secrets.h"

Adafruit_MPU6050 mpu;

// ESP32 DevKit V1 pin map
const int BANK_TRIG = 16;
const int BANK_ECHO = 18;   // Use a voltage divider before this pin
const int RIVER_TRIG = 19;
const int RIVER_ECHO = 23; // Use a voltage divider before this pin
const int SOIL_PIN = 34;
const int FLOW_PIN = 27;   // Optional YF-S201 flow sensor

const int GREEN_LED = 32;
const int YELLOW_LED = 33;
const int RED_LED = 13;
const int BUZZER_PIN = 25;

// Calibrate these values for your own model.
const float BANK_BASELINE_CM = 10.0;
const float TILT_BASELINE_DEG = 0.0;
const float RIVER_SENSOR_HEIGHT_CM = 15.0;
const int SOIL_DRY_RAW = 3000;
const int SOIL_WET_RAW = 1400;
const float FLOW_PULSES_PER_LITER = 450.0;
const bool USE_FLOW_SENSOR = true;

// ThingSpeak free service accepts one channel update every 15 seconds.
// Use 20 seconds to stay above the minimum interval.
const unsigned long UPLOAD_INTERVAL_MS = 20000;
const unsigned long SENSOR_INTERVAL_MS = 1000;

volatile unsigned long flowPulses = 0;
unsigned long lastUpload = 0;
unsigned long lastSensorRead = 0;
unsigned long lastFlowRead = 0;

float bankDistanceCm = 0;
float riverDistanceCm = 0;
float tiltDeg = 0;
float soilMoisturePct = 0;
float flowLpm = 0;
bool mpuReady = false;
bool bankSensorValid = false;
bool riverSensorValid = false;

void IRAM_ATTR countFlowPulse() {
  flowPulses++;
}

float readUltrasonicCm(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(3);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  unsigned long duration = pulseIn(echoPin, HIGH, 30000);
  if (duration == 0) return -1.0;

  return duration * 0.0343 / 2.0;
}

float readSoilMoisturePercent() {
  int raw = analogRead(SOIL_PIN);
  long percent = map(raw, SOIL_DRY_RAW, SOIL_WET_RAW, 0, 100);
  return constrain(percent, 0, 100);
}

float readTiltDegrees() {
  if (!mpuReady) return 0.0;

  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  float angle = atan2(accel.acceleration.y, accel.acceleration.z) * 180.0 / PI;
  return angle;
}

void updateFlowRate() {
  if (!USE_FLOW_SENSOR) {
    flowLpm = 0.0;
    return;
  }

  unsigned long now = millis();
  if (now - lastFlowRead >= 1000) {
    noInterrupts();
    unsigned long pulses = flowPulses;
    flowPulses = 0;
    interrupts();

    float seconds = (now - lastFlowRead) / 1000.0;
    flowLpm = (pulses / FLOW_PULSES_PER_LITER) * 60.0 / seconds;
    lastFlowRead = now;
  }
}

void readAllSensors() {
  float bankReading = readUltrasonicCm(BANK_TRIG, BANK_ECHO);
  float riverReading = readUltrasonicCm(RIVER_TRIG, RIVER_ECHO);

  bankSensorValid = bankReading > 0;
  riverSensorValid = riverReading > 0;

  if (bankSensorValid) bankDistanceCm = bankReading;
  if (riverSensorValid) riverDistanceCm = riverReading;

  soilMoisturePct = readSoilMoisturePercent();
  tiltDeg = readTiltDegrees();
  updateFlowRate();

  Serial.println("------ BANKGUARD BD SENSOR DATA ------");
  Serial.printf("Bank distance: %.2f cm\n", bankDistanceCm);
  Serial.printf("Slope tilt: %.2f degree\n", tiltDeg);
  Serial.printf("Soil moisture: %.1f %%\n", soilMoisturePct);
  Serial.printf("River distance: %.2f cm\n", riverDistanceCm);
  Serial.printf("Flow rate: %.2f L/min\n", flowLpm);
}

void updateLocalAlerts() {
  float retreat = bankDistanceCm - BANK_BASELINE_CM;
  float tiltChange = fabs(tiltDeg - TILT_BASELINE_DEG);

  bool critical = (retreat >= 4.0 && tiltChange >= 8.0);
  bool warning = (retreat >= 1.0 || tiltChange >= 3.0 || soilMoisturePct >= 75.0);

  digitalWrite(GREEN_LED, (!warning && !critical) ? HIGH : LOW);
  digitalWrite(YELLOW_LED, (warning && !critical) ? HIGH : LOW);
  digitalWrite(RED_LED, critical ? HIGH : LOW);
  digitalWrite(BUZZER_PIN, critical ? HIGH : LOW);
}

bool uploadToThingSpeak() {
  if (!bankSensorValid || !riverSensorValid || !mpuReady) {
    Serial.println("One or more required sensors are not ready. Cloud upload skipped.");
    return false;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    WiFi.reconnect();
    return false;
  }

  WiFiClientSecure client;
  // Beginner prototype setting: HTTPS encryption is used, but the server
  // certificate is not verified. Use a valid root CA certificate in production.
  client.setInsecure();

  HTTPClient http;

  String url = "https://api.thingspeak.com/update?api_key=";
  url += THINGSPEAK_WRITE_API_KEY;
  url += "&field1=" + String(bankDistanceCm, 2);
  url += "&field2=" + String(tiltDeg, 2);
  url += "&field3=" + String(soilMoisturePct, 1);
  url += "&field4=" + String(riverDistanceCm, 2);
  url += "&field5=" + String(flowLpm, 2);

  if (!http.begin(client, url)) {
    Serial.println("Could not start HTTPS request.");
    return false;
  }

  int httpCode = http.GET();
  String response = http.getString();
  http.end();

  Serial.printf("ThingSpeak HTTP code: %d, response: %s\n",
                httpCode, response.c_str());

  // ThingSpeak returns a positive entry number when an update is accepted.
  return (httpCode == 200 && response.toInt() > 0);
}

void setup() {
  Serial.begin(115200);

  pinMode(BANK_TRIG, OUTPUT);
  pinMode(BANK_ECHO, INPUT);
  pinMode(RIVER_TRIG, OUTPUT);
  pinMode(RIVER_ECHO, INPUT);

  pinMode(SOIL_PIN, INPUT);
  pinMode(FLOW_PIN, INPUT_PULLUP);

  pinMode(GREEN_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(RED_LED, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  analogReadResolution(12);

  Wire.begin(21, 22);
  mpuReady = mpu.begin();

  if (mpuReady) {
    mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("MPU6050 ready.");
  } else {
    Serial.println("MPU6050 not found. Check SDA=21, SCL=22, power and GND.");
  }

  if (USE_FLOW_SENSOR) {
    attachInterrupt(digitalPinToInterrupt(FLOW_PIN), countFlowPulse, RISING);
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Wi-Fi connected. IP: ");
  Serial.println(WiFi.localIP());

  lastUpload = millis();
  lastSensorRead = millis();
  lastFlowRead = millis();
}

void loop() {
  unsigned long now = millis();

  if (now - lastSensorRead >= SENSOR_INTERVAL_MS) {
    lastSensorRead = now;
    readAllSensors();
    updateLocalAlerts();
  }

  if (now - lastUpload >= UPLOAD_INTERVAL_MS) {
    lastUpload = now;
    bool ok = uploadToThingSpeak();
    Serial.println(ok ? "Cloud upload accepted." : "Cloud upload failed or rejected.");
  }

  delay(5);
}
