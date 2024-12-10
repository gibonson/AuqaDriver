#include <ESP8266WiFi.h>        // Load Wi-Fi library
#include <ESP8266HTTPClient.h>  // HTTP client for ESP8266
#include <HttpClient.h>         // HTTP client library

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

#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define OLED_RESET     -1   // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C // If not work please try 0x3D
#define OLED_SDA D5         // Stock firmware shows wrong pins
#define OLED_SCL D6         // They swap SDA with SCL ;)
int c = 0; // uptime counter
Adafruit_SSD1306 *display;

#define CONFIG_TIMEOUT 2000  // Czas oczekiwania na dane (2 sekundy)


void init_oled() {
  display = new Adafruit_SSD1306(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

  // OLED used nonstandard SDA and SCL pins
  Wire.begin(D5, D6);
  
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display->begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    return;
  }
}

void handle_oled(String value1, String value2, String value3, String value4, String value5, String value6, String value7, String value8) {
  display->clearDisplay();
  display->setTextSize(1);
  display->setTextColor(SSD1306_WHITE);
  display->setCursor(0, 0);

  display->println(value1);
  display->println(value2);
  display->println(value3);
  display->println(value4);
  display->println(value5);
  display->println(value6);
  display->println(value7);
  display->println(value8);
  display->println(c);

  display->display();
}


//////  config 
// Funkcja obsługująca tryb konfiguracji
void konfiguracja() {
  Serial.println("Wprowadź dane konfiguracji:");
  while (true) {
    if (Serial.available() > 0) {
      String dane = Serial.readString();
      Serial.print("Otrzymano: ");
      Serial.println(dane);
      break; // Zakończenie konfiguracji
    }
  }
}
void standardowyKod() {
  Serial.println("Standardowy kod uruchomiony.");
  // Dodaj tutaj logikę standardowego programu
}
///////

void setup() {
  Serial.begin(9600);

  Serial.println("Uruchamianie...");
  
  unsigned long startTime = millis(); // Pobranie aktualnego czasu
  bool configMode = false;            // Flaga trybu konfiguracji

  // Czekanie na dane przez 2 sekundy
  while (millis() - startTime < CONFIG_TIMEOUT) {
    if (Serial.available() > 0) {
      configMode = true;  // Wykryto dane
      break;
    }
  }

//////  config 
  if (configMode) {
    Serial.println("Tryb konfiguracji...");
    konfiguracja(); // Wywołanie funkcji konfiguracji
  } else {
    Serial.println("Uruchamianie standardowego kodu...");
    standardowyKod(); // Wywołanie standardowego kodu
  }
}
//////  

  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  } else {
    Serial.println("CONF OK");
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

void sendJson(String addInfo, int value, String type) {
  http.begin(client, serverName);
  http.addHeader("Content-Type", "application/json");
  String jsonString = "{\"deviceIP\":\"" +
                      String(local_IP[0]) + "." +
                      String(local_IP[1]) + "." +
                      String(local_IP[2]) + "." +
                      String(local_IP[3]) +
                      "\",\"deviceName\":\"" + deviceName +
                      "\",\"addInfo\":\"" + addInfo +
                      "\",\"type\":\"" + type +
                      "\",\"value\":" + String(value) + "}";
  Serial.println("Json to sent: " + jsonString);
  Serial.println(http.POST(jsonString));
}

void loop() {
  WebGui webGui;

  //  delay(5000);
  WiFiClient client = server.available();  // Listen for incoming clients

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
              client.print(webGui.generator(webTable));
              client.stop();    // Close the connection
            }
            else if (header.indexOf("noGui") >= 0) {
              client.print(webGui.noGui(webTable));
              client.stop();    // Close the connection
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

              resultHtml += webGui.resultLogContent(0, "Fertilizers req");
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
              
              handle_oled(value1, value2, value3, value4, value5, value6 ,value7 ,value8);
              sendJson("LCD" , 0 , "Log");
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
