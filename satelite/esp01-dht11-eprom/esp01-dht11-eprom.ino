// Include necessary libraries
#include <ESP8266WiFi.h>        // Load Wi-Fi library
#include <ESP8266HTTPClient.h>  // HTTP client for ESP8266
#include <HttpClient.h>         // HTTP client library
#include <DHT.h>                // DHT sensor library
#include <RCSwitch.h>           // RF remote control library
#include <OneWire.h>            // OneWire library
#include <DallasTemperature.h>  // DS18B20 Dallas Temperature library

// Include custom headers
#include "WebGui.h"             // Custom Web GUI library
#include "configuration.h"      // Configuration header

// Wi-Fi and HTTP configuration
String header;                         // Variable to store the HTTP request
HTTPClient http;                       // HTTP client instance
WiFiClient client;                     // Wi-Fi client instance
String sthToSend = "";                 // Data to send over HTTP

// Wi-Fi Timing variables
unsigned long currentTime = millis();  // Current time
unsigned long previousTime = 0;        // Previous time
const long timeoutTime = 500;          // Timeout time in milliseconds

// DHT sensor setup
#define DHTTYPE DHT22                  // DHT22 - DHT 22(AM2302)
const int DHT_PIN = 4;                 // GPIO4 = D2 Digital pin connected to the DHT sensor
DHT dht(DHT_PIN, DHTTYPE);             // Initialize DHT sensor

// DS18B20 sensor setup
const int ONE_WIRE_BUS = 16;           // GPIO16 = D0 pin connected to the  sensor
OneWire oneWire(ONE_WIRE_BUS);         // Setup a oneWire instance to communicate with any OneWire devices
DallasTemperature sensors(&oneWire);   // Pass our oneWire reference to Dallas Temperature sensor 

// RF remote control setup
RCSwitch mySwitch = RCSwitch();        // Initialize RF switch
const int RC_TRANSMITER_PIN = 0;       // GPIO0 = D3 Transmitter data pin

// Pin configuration
const int LED_PIN_1 = 2;               // GPIO2 = D4 = ESP LED - LED_PIN_1 
const int LED_PIN_2 = 12;              // GPIO12= D6 - Relay 1 control pin
const int LED_PIN_3 = 13;              // GPIO13= D7 - Relay 2 control pin
const int LED_PIN_4 = 15;              // GPIO15= D8 - Relay 3 control pin
const int LED_PIN_5 = 3;               // GPIO5 = RX - Relay 4 control pin

const int LED_PIN_ALERT = 5;           // GPIO5 = D1 - Status LED 
const int MOTION_SENSOR = 14;          // GPIO14 = D5 - Motion Sensor 

// Constant strings
const String ALERT_NAME = "Ruch";  // Alert name for button

// Checks if motion was detected
ICACHE_RAM_ATTR void detectsMovement() {
  Serial.println("Alert!!!");
  sthToSend = "yes";
  pinMode(LED_PIN_ALERT, OUTPUT); // Set LED to LOW
  digitalWrite(LED_PIN_ALERT, LOW);
  analogWrite(LED_PIN_ALERT, 5);
}

void setup() {
  Serial.begin(9600);

  //ser led pin to output
  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);
  pinMode(LED_PIN_4, OUTPUT);
  pinMode(LED_PIN_5, OUTPUT);

  mySwitch.enableTransmit(RC_TRANSMITER_PIN); // Transmitter is connected to Arduino Pin #0
  mySwitch.setProtocol(1);  // Optional set protocol (default is 1, will work for most outlets)
  mySwitch.setPulseLength(350); // Optional set pulse length.
  // mySwitch.setRepeatTransmit(15);  // Optional set number of transmission repetitions.

  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  } else {
    Serial.println("CONF OK");
  }
  // Connect to Wi-Fi network with SSID and password
  Serial.print("Connecting to ");
  Serial.println(String(ssid));
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  // Print local IP address and start web server
  Serial.println("");
  Serial.println("WiFi connected. IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("");
  server.begin();

  delay(500);
  dht.begin();
  float newT = dht.readTemperature();
  float newH = dht.readHumidity();
  if (isnan(newT)) {
    Serial.println("Failed to read from DHT sensor!");
  }

  pinMode(MOTION_SENSOR, INPUT_PULLUP);  // PIR Motion Sensor mode INPUT_PULLUP
  // Set motionSensor pin as interrupt, assign interrupt function and set RISING mode
  attachInterrupt(digitalPinToInterrupt(MOTION_SENSOR), detectsMovement, RISING);
  pinMode(LED_PIN_ALERT, OUTPUT); // Set LED to LOW
  digitalWrite(LED_PIN_ALERT, LOW);
}

void loop() {
  WebGui webGui;
  delay(5000);
  WiFiClient client = server.available();  // Listen for incoming clients
  if (sthToSend == "yes") {
    Serial.println("zamiana");
    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");
    String jsonString = "{\"addInfo\":\"" + ALERT_NAME + "\",\"deviceIP\":\"" + local_IP[0] + "." + local_IP[1] + "." + local_IP[2] + "." + local_IP[3] + "\",\"deviceName\":\"" + deviceName + "\",\"type\":\"Alert\",\"value\":1}";
    int httpResponseCode = http.POST(jsonString);
    Serial.println(httpResponseCode);
    sthToSend = "";
  }


  if (client) {
    Serial.println();
    Serial.println("New Client.");  // print a message out in the serial port
    String currentLine = "";        // make a String to hold incoming data from the client

    while (client.connected()) {  // loop while the client's connected
      if (client.available()) {  // if there's bytes to read from the client,
        char c = client.read();  // read a byte, then
        Serial.write(c);         // print it out the serial monitor
        header += c;
        if (c == '\n') {  // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            Serial.println("HTTP / 1.1 200 OK"); // HTTP headers always start with a response code (e.g. HTTP/ 1.1 200 OK)
            Serial.println("Content - type: text / html"); // and a content-type so the client knows what's coming, then a blank line:
            Serial.println("Connection: close");
            // Serial.println(header);

            if (header.indexOf("GET / HTTP/1.1") >= 0) {
              sensors.requestTemperatures(); 
              float temperature_Celsius = sensors.getTempCByIndex(0);
              float newT = dht.readTemperature();
              float newH = dht.readHumidity();
              webContent[1][2] = String(newT);
              webContent[2][2] = String(newH);
              webContent[3][2] = String(temperature_Celsius);
              client.print(webGui.generator(webContent));
            }
            else if (header.indexOf("noGui") >= 0) {
              float newT = dht.readTemperature();
              float newH = dht.readHumidity();
              //              if (isnan(newT)) {
              //                Serial.println("Failed to read from DHT sensor!");
              //              }
              webContent[1][2] = String(newT);
              webContent[2][2] = String(newH);
              client.print(webGui.noGui(webContent));
            }
            else if (header.indexOf("GET /nawozy") >= 0) {
              ///http://192.168.0.184/test1?name1=value1&name2=value2&name2=value2
              int start = header.indexOf(" ? ");
              int var1Start = header.indexOf("value1=");
              int var1Stop = header.indexOf("&", 0);
              int var2Start = header.indexOf("value2=");
              int var2Stop = header.indexOf("&", var1Stop + 1);
              int var3Start = header.indexOf("value3=");
              int var3Stop = header.indexOf("&", var2Stop + 1);
              int var4Start = header.indexOf("value4=");
              int var4Stop = header.indexOf(" HTTP/1.1");

              int value1 = header.substring(var1Start + 7, var1Stop).toInt();
              int value2 = header.substring(var2Start + 7, var2Stop).toInt();
              int value3 = header.substring(var3Start + 7, var3Stop).toInt();
              int value4 = header.substring(var4Start + 7, var4Stop).toInt();

              // Serial.println("Value1 position: " +  String(var1Start) + " - " +  String(var1Stop) + ", value1 = " +  String(value1));
              // Serial.println("Value2 position: " +  String(var2Start) + " - " +  String(var2Stop) + ", value2 = " +  String(value2));
              // Serial.println("Value3 position: " +  String(var3Start) + " - " +  String(var3Stop) + ", value3 = " +  String(value3));
              // Serial.println("Value4 position: " +  String(var4Start) + " - " +  String(var4Stop) + ", value4 = " +  String(value4));

              digitalWrite(LED_PIN_2, HIGH);  // turn the LED on
              delay(value1 * 1000);
              digitalWrite(LED_PIN_2, LOW);  // turn the LED off
              delay(100);

              digitalWrite(LED_PIN_3, HIGH);  // turn the LED on
              delay(value2 * 1000);
              digitalWrite(LED_PIN_3, LOW);  // turn the LED off
              delay(100);

              digitalWrite(LED_PIN_4, HIGH);  // turn the LED on
              delay(value3 * 1000);
              digitalWrite(LED_PIN_4, LOW);  // turn the LED off
              delay(100);

              digitalWrite(LED_PIN_5, HIGH);  // turn the LED on
              delay(value4 * 1000);
              digitalWrite(LED_PIN_5, LOW);  // turn the LED off
              delay(100);
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(value1, "Mikroelementy [s]");
              resultHtml = resultHtml + webGui.resultLogContent(value2, "Makroelementy [s]");
              resultHtml = resultHtml + webGui.resultLogContent(value3, "Carbo [s]");
              resultHtml = resultHtml + webGui.resultLogContent(value4, "Jack Daniels [s]");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            }
            else if (header.indexOf("GET /gpioON") >= 0) {
              digitalWrite(LED_PIN_1, HIGH);  // turn the LED on
              digitalWrite(LED_PIN_2, HIGH);  // turn the LED on
              digitalWrite(LED_PIN_3, HIGH);  // turn the LED on
              digitalWrite(LED_PIN_4, HIGH);  // turn the LED on
              digitalWrite(LED_PIN_5, HIGH);  // turn the LED on
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(1, "Mikroelementy - stan");
              resultHtml = resultHtml + webGui.resultLogContent(1, "Makroelementy - stan");
              resultHtml = resultHtml + webGui.resultLogContent(1, "Carbo - stan");
              resultHtml = resultHtml + webGui.resultLogContent(1, "Jack Daniels - stan");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            }
            else if (header.indexOf("GET /gpioOFF") >= 0) {
              digitalWrite(LED_PIN_1, LOW);  // turn the LED off
              digitalWrite(LED_PIN_2, LOW);  // turn the LED off
              digitalWrite(LED_PIN_3, LOW);  // turn the LED off
              digitalWrite(LED_PIN_4, LOW);  // turn the LED off
              digitalWrite(LED_PIN_5, LOW);  // turn the LED off
              digitalWrite(LED_PIN_ALERT, LOW); // turn off ALERT LED
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(0, "Mikroelementy - stan");
              resultHtml = resultHtml + webGui.resultLogContent(0, "Makroelementy - stan");
              resultHtml = resultHtml + webGui.resultLogContent(0, "Carbo - stan");
              resultHtml = resultHtml + webGui.resultLogContent(0, "Jack Daniels - stan");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            } else if (header.indexOf("GET /socket1ON") >= 0) {
              mySwitch.send(4433, 24);
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(1, "S1 - stan");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            } else if (header.indexOf("GET /socket1OFF") >= 0) {
              mySwitch.send(4436, 24);
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(0, "S1 - stan");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            } else if (header.indexOf("GET /socket2ON") >= 0) {
              mySwitch.send(5201, 24);
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(1, "S2 - stan");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            } else if (header.indexOf("GET /socket2OFF") >= 0) {
              mySwitch.send(5204, 24);
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(0, "S2 - stan");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            } else if (header.indexOf("GET /socket3ON") >= 0) {
              mySwitch.send(5393, 24);
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(1, "S3 - stan");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            } else if (header.indexOf("GET /socket3OFF") >= 0) {
              mySwitch.send(5396, 24);
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(0, "S3 - stan");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            } else {
              String resultHtml = "";
              resultHtml = webGui.resultLogBegin(deviceName);
              resultHtml = resultHtml + webGui.resultLogContent(0, "Not Found");
              resultHtml = resultHtml + webGui.resultLogEnd();
              client.print(resultHtml);
            }
            break;
          } else {  // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    // Clear the header variable
    header = "";
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  }
}
