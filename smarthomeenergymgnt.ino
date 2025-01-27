#include <ESP8266WiFi.h>  // Include for ESP8266; use <WiFi.h> for ESP32
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN 2         // DHT sensor connected to GPIO2 (D4 on NodeMCU)
#define DHTTYPE DHT22    // DHT 22 (AM2302)
#define MOTION_PIN 5     // PIR sensor connected to GPIO5 (D1 on NodeMCU)
#define FAN_PIN 4        // Relay controlling the fan connected to GPIO4 (D2 on NodeMCU)

const char* ssid = "your-SSID";         // Replace with your Wi-Fi SSID
const char* password = "your-PASSWORD"; // Replace with your Wi-Fi password
const char* mqtt_server = "mqtt.eclipse.org"; // Public MQTT broker (or use your own)

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(10);

  pinMode(MOTION_PIN, INPUT);  // Motion sensor input
  pinMode(FAN_PIN, OUTPUT);    // Relay controlling the fan

  // Connect to Wi-Fi
  setup_wifi();

  // Set up MQTT
  client.setServer(mqtt_server, 1883);
  
  // Initialize DHT sensor
  dht.begin();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read sensor data
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Read motion detection
  int motionDetected = digitalRead(MOTION_PIN);

  // If readings are valid, send them via MQTT
  if (!isnan(humidity) && !isnan(temperature)) {
    // Publish sensor data to MQTT
    char tempStr[8];
    dtostrf(temperature, 6, 2, tempStr);
    client.publish("home/smart/temperature", tempStr);

    char humStr[8];
    dtostrf(humidity, 6, 2, humStr);
    client.publish("home/smart/humidity", humStr);
  }

  // Publish motion detection status
  char motionStr[2];
  itoa(motionDetected, motionStr, 10);
  client.publish("home/smart/motion", motionStr);

  // Control fan based on motion
  if (motionDetected == HIGH) {
    digitalWrite(FAN_PIN, HIGH);  // Turn fan on
    client.publish("home/smart/fan", "ON");
  } else {
    digitalWrite(FAN_PIN, LOW);   // Turn fan off
    client.publish("home/smart/fan", "OFF");
  }

  delay(2000);  // Delay for 2 seconds before taking new readings
}

// Wi-Fi connection function
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi...");
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.print("Connected to WiFi! IP address: ");
  Serial.println(WiFi.localIP());
}

// MQTT reconnect function
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      
      // Once connected, subscribe to topics (optional)
      client.subscribe("home/smart/fan");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
