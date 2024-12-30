#include <Arduino.h>
#include <Wire.h>

// ESP filesystem libraries
#include <FS.h>
#include <LittleFS.h>

// Wi-Fi and HTTP libraries
#include <ESP8266WiFi.h>        // Load Wi-Fi library
#include <ESP8266HTTPClient.h>  // HTTP client for ESP8266
#include <HttpClient.h>         // HTTP client library

//LCD libraries
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <DHT.h>                // DHT sensor library
#include <RCSwitch.h>           // RF remote control library
#include <OneWire.h>            // OneWire library
#include <DallasTemperature.h>  // DS18B20 Dallas Temperature library

// Wi-Fi and HTTP configuration
#define CONFIG_TIMEOUT 5000  // Data waiting time
String header;                         // Variable to store the HTTP request
HTTPClient http;                       // HTTP client instance
WiFiClient client;                     // Wi-Fi client instance
String sthToSend = "";                 // Data to send over HTTP
unsigned long currentTime = millis();  // Current time
unsigned long previousTime = 0;        // Previous time
const long timeoutTime = 500;          // Timeout time in milliseconds

// LCD Configuration
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET     -1   // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C // If not work please try 0x3D
#define OLED_SDA D5         // Stock firmware shows wrong pins
#define OLED_SCL D6         // They swap SDA with SCL ;)
Adafruit_SSD1306 *display;


// DHT sensor setup
#define DHTTYPE DHT22                  // DHT22 - DHT 22(AM2302)
const int DHT_PIN = 4;                 // GPIO4 = D2 Digital pin connected to the DHT sensor
DHT dht(DHT_PIN, DHTTYPE);             // Initialize DHT sensor

// DS18B20 sensor setup
const int ONE_WIRE_BUS = 16;           // GPIO16 = D0 pin connected to the  sensor
OneWire oneWire(ONE_WIRE_BUS);         // Setup a oneWire instance to communicate with any OneWire devices
DallasTemperature sensors(&oneWire);   // Pass our oneWire reference to Dallas Temperature sensor

// RF 433 remote control setup
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


// ESP filesystem libraries
const char *configFilePath = "/config.txt"; // Configuration path on device

// Project files
#include "Configuration.h"      // Configuration header
#include "JsonOperation.h"
#include "OledOperation.h"
#include "WebGui.h"             // Custom Web GUI library



// Checks if motion was detected
ICACHE_RAM_ATTR void detectsMovement() {
  Serial.println("Interrupt!!!");
  sthToSend = "yes";
  pinMode(LED_PIN_ALERT, OUTPUT); // Set LED to LOW
  digitalWrite(LED_PIN_ALERT, LOW);
  analogWrite(LED_PIN_ALERT, 5);
}



void setup() {
  delay(100);
  Serial.begin(9600);
  Serial.println("\nDevice starting - configuration...\n");

  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);
  pinMode(LED_PIN_4, OUTPUT);
  pinMode(LED_PIN_5, OUTPUT);

  pinMode(MOTION_SENSOR, INPUT_PULLUP);  // PIR Motion Sensor mode INPUT_PULLUP
  attachInterrupt(digitalPinToInterrupt(MOTION_SENSOR), detectsMovement, RISING); // Set motionSensor pin as interrupt, assign interrupt function and set RISING mode

  pinMode(LED_PIN_ALERT, OUTPUT); // Set LED to LOW
  digitalWrite(LED_PIN_ALERT, LOW);

  mySwitch.enableTransmit(RC_TRANSMITER_PIN); // Transmitter is connected to Arduino Pin #0
  mySwitch.setProtocol(1);  // Optional set protocol (default is 1, will work for most outlets)
  mySwitch.setPulseLength(350); // Optional set pulse length.
  // mySwitch.setRepeatTransmit(15);  // Optional set number of transmission repetitions.


  // Initializing LittleFS
  if (!LittleFS.begin()) {
    Serial.println("LittleFS initialization error!");
    return;
  }

  // Checking if the configuration file exists
  if (LittleFS.exists(configFilePath)) {
    Serial.println("Loading configuration:");
    readSettings();
    Serial.println("\nIf you want to change something, type any character and press enter in the console...");
  } else {
    Serial.println("No settings saved. Starting configuration...");
    deviceConfiguration();
  }

  unsigned long startTime = millis();
  bool configMode = false;

  // Waiting for data for CONFIG_TIMEOUT/1000
  while (millis() - startTime < CONFIG_TIMEOUT) {
    if (Serial.available() > 0) {
      Serial.readStringUntil('\n');
      configMode = true;
      break; // go to config mode
    }
  }

  if (configMode) {
    Serial.println("Configuration Mode...");
    deviceConfiguration();
  } else {
    Serial.println("Device starting");
  }

  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  } else {
    Serial.println("Wifi configuration - OK");
  }
  Serial.println("Connecting to " + String(ssid));
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("\nWiFi connected. IP address: "); // Print local IP address and start web server
  Serial.println(WiFi.localIP()); // Print local IP address and start web server
  Serial.println("");
  server.begin();

  delay(500);
  init_oled();
  sendJson("Device Start", 1, "Log");
}


void readSensors() {
  sensors.requestTemperatures();
  float temperature_Celsius = sensors.getTempCByIndex(0);
  float newT = dht.readTemperature();
  float newH = dht.readHumidity();
  //  if (isnan(newT)) {
  //    Serial.println("Failed to read from  sensor!");
  //    sendJson("DHT issue" , 1 , "Error");
  //  }
  webTableSTD[1][2] = String(newT);
  webTableSTD[2][2] = String(newH);
  webTableSTD[3][2] = String(temperature_Celsius);
}

void loop() {
  WebGui webGui;
  WiFiClient client = server.available();  // Listen for incoming clients

  if (sthToSend == "yes") {
    Serial.println("zamiana");
    sendJson("Motion" , 1 , "Alert");
    sthToSend = "";
  }

  if (client) {
    Serial.println("\nNew Client.");  // print a message out in the serial port
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
            String resultHtml = webGui.resultLogBegin();
            if (header.indexOf("GET / HTTP/1.1") >= 0) {
              if (deviceType == "LCD") {
                client.print(webGui.generator(webTableLCD));
              } else {
                client.print(webGui.generator(webTableSTD));
              }
              client.stop();    // Close the connection
            }
            else if (header.indexOf("noGui") >= 0) {
              if (deviceType == "LCD") {
                client.print(webGui.generator(webTableLCD));
              } else {
                client.print(webGui.generator(webTableSTD));
              }
              client.stop();    // Close the connection
            }
            else if (header.indexOf("GET /lcd") >= 0) {
              int start = header.indexOf(" ? ");
              int var1Start = header.indexOf("value1=");
              int var1Stop = header.indexOf("&", 0);
              int var2Start = header.indexOf("value2=");
              int var2Stop = header.indexOf("&", var1Stop + 1);
              int var3Start = header.indexOf("value3=");
              int var3Stop = header.indexOf("&", var2Stop + 1);
              int var4Start = header.indexOf("value4=");
              int var4Stop = header.indexOf("&", var3Stop + 1);
              int var5Start = header.indexOf("value5=");
              int var5Stop = header.indexOf("&", var4Stop + 1);
              int var6Start = header.indexOf("value6=");
              int var6Stop = header.indexOf("&", var5Stop + 1);
              int var7Start = header.indexOf("value7=");
              int var7Stop = header.indexOf("&", var6Stop + 1);
              int var8Start = header.indexOf("value8=");
              int var8Stop = header.indexOf(" HTTP/1.1");

              String value1 = header.substring(var1Start + 7, var1Stop);
              String value2 = header.substring(var2Start + 7, var2Stop);
              String value3 = header.substring(var3Start + 7, var3Stop);
              String value4 = header.substring(var4Start + 7, var4Stop);
              String value5 = header.substring(var5Start + 7, var5Stop);
              String value6 = header.substring(var6Start + 7, var6Stop);
              String value7 = header.substring(var7Start + 7, var7Stop);
              String value8 = header.substring(var8Start + 7, var8Stop);

              resultHtml += webGui.resultLogContent(0, "lcd log");
              resultHtml += webGui.RESULT_LOG_END;
              client.print(resultHtml);
              client.stop();    // Close the connection


              value1 = "IP:" + String(local_IP[0]) + "." + String(local_IP[1]) + "." + String(local_IP[2]) + "." + String(local_IP[3]);
              value2 = WiFi.status();
              //    WL_IDLE_STATUS      = 0,
              //    WL_NO_SSID_AVAIL    = 1,
              //    WL_SCAN_COMPLETED   = 2,
              //    WL_CONNECTED        = 3,
              //    WL_CONNECT_FAILED   = 4,
              //    WL_CONNECTION_LOST  = 5,
              //    WL_DISCONNECTED     = 6

              handle_oled(value1, value2, value3, value4, value5, value6 , value7 , value8);
              sendJson("LCD" , 0 , "Log");
            }

            else if (header.indexOf("GET /nawozy") >= 0) {
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

              resultHtml += webGui.resultLogContent(0, "Fertilizers req");
              resultHtml += webGui.RESULT_LOG_END;
              client.print(resultHtml);
              client.stop();    // Close the connection

              digitalWrite(LED_PIN_2, HIGH);  // turn the LED on
              delay(value1 * 1000);
              digitalWrite(LED_PIN_2, LOW);  // turn the LED off
              delay(100);
              sendJson("Mikro [s]" , value1 , "Log");

              digitalWrite(LED_PIN_3, HIGH);  // turn the LED on
              delay(value2 * 1000);
              digitalWrite(LED_PIN_3, LOW);  // turn the LED off
              delay(100);
              sendJson("Makro [s]" , value2 , "Log");

              digitalWrite(LED_PIN_4, HIGH);  // turn the LED on
              delay(value3 * 1000);
              digitalWrite(LED_PIN_4, LOW);  // turn the LED off
              delay(100);
              sendJson("Carbo [s]" , value3 , "Log");

              digitalWrite(LED_PIN_5, HIGH);  // turn the LED on
              delay(value4 * 1000);
              digitalWrite(LED_PIN_5, LOW);  // turn the LED off
              delay(100);
              sendJson("Jack [s]" , value4 , "Log");
            }
            else if (header.indexOf("GET /gpioON") >= 0) {
              digitalWrite(LED_PIN_1, HIGH);  // turn the LED on
              digitalWrite(LED_PIN_2, HIGH);  // turn the LED on
              digitalWrite(LED_PIN_3, HIGH);  // turn the LED on
              digitalWrite(LED_PIN_4, HIGH);  // turn the LED on
              digitalWrite(LED_PIN_5, HIGH);  // turn the LED on
              resultHtml += webGui.resultLogContent(1, "Mikroelementy - stan");
              resultHtml += webGui.resultLogContent(1, "Makroelementy - stan");
              resultHtml += webGui.resultLogContent(1, "Carbo - stan");
              resultHtml += webGui.resultLogContent(1, "Jack Daniels - stan");
            }
            else if (header.indexOf("GET /gpioOFF") >= 0) {
              digitalWrite(LED_PIN_1, LOW);  // turn the LED off
              digitalWrite(LED_PIN_2, LOW);  // turn the LED off
              digitalWrite(LED_PIN_3, LOW);  // turn the LED off
              digitalWrite(LED_PIN_4, LOW);  // turn the LED off
              digitalWrite(LED_PIN_5, LOW);  // turn the LED off
              digitalWrite(LED_PIN_ALERT, LOW); // turn off ALERT LED
              resultHtml += webGui.resultLogContent(0, "Mikroelementy - stan");
              resultHtml += webGui.resultLogContent(0, "Makroelementy - stan");
              resultHtml += webGui.resultLogContent(0, "Carbo - stan");
              resultHtml += webGui.resultLogContent(0, "Jack Daniels - stan");
            }
            else if (header.indexOf("GET /socket1ON") >= 0) {
              mySwitch.send(4433, 24);
              resultHtml += webGui.resultLogContent(1, "S1 - stan");
            }
            else if (header.indexOf("GET /socket1OFF") >= 0) {
              mySwitch.send(4436, 24);
              resultHtml += webGui.resultLogContent(0, "S1 - stan");
            } else if (header.indexOf("GET /socket2ON") >= 0) {
              mySwitch.send(5201, 24);
              resultHtml += webGui.resultLogContent(1, "S2 - stan");
            }
            else if (header.indexOf("GET /socket2OFF") >= 0) {
              mySwitch.send(5204, 24);
              resultHtml += webGui.resultLogContent(0, "S2 - stan");
            }
            else if (header.indexOf("GET /socket3ON") >= 0) {
              mySwitch.send(5393, 24);
              resultHtml += webGui.resultLogContent(1, "S3 - stan");
            }
            else if (header.indexOf("GET /socket3OFF") >= 0) {
              mySwitch.send(5396, 24);
              resultHtml += webGui.resultLogContent(0, "S3 - stan");
            }
            else {
              resultHtml += webGui.resultLogContent(0, "Not Found");
            }
            resultHtml = resultHtml + webGui.RESULT_LOG_END;
            client.print(resultHtml);
            break;
          } else {  // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    header = "";      // Clear the header variable
    client.stop();    // Close the connection
    Serial.println("Client disconnected.\n");
  }
}
