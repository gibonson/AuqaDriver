#include <Arduino.h>
#include <LittleFS.h>    // ESP file system libraries, which store the Wi-Fi configuration file, device name, type and server address (json)
#include <ArduinoJson.h> // JSON library for Arduino, used to create and parse JSON objects

#include <DHT.h>     // DHT sensor library
#include <OneWire.h> // OneWire library
// #include <RCSwitch.h>           // RF remote control library to fix
#include <DallasTemperature.h> // DS18B20 Dallas Temperature library

// Project files
#include "Configuration.h"
#include "WifiOperation.h"
#include "JsonOperation.h"
#include "OledOperation.h"
#include "WebGui.h"
String logBuffer = "";

const int LED_PIN_1 = 2;  // GPIO2 = D4 = ESP LED - LED_PIN_1
const int LED_PIN_2 = 12; // GPIO12= D6 - Relay 1 control pin
const int LED_PIN_3 = 13; // GPIO13= D7 - Relay 2 control pin
const int LED_PIN_4 = 15; // GPIO15= D8 - Relay 3 control pin
const int LED_PIN_5 = 3;  // GPIO5 = RX - Relay 4 control pin

// DS18B20 sensor setup
const int ONE_WIRE_BUS = 16;         // GPIO16 = D0 pin connected to the  sensor
OneWire oneWire(ONE_WIRE_BUS);       // Setup a oneWire instance to communicate with any OneWire devices
DallasTemperature sensors(&oneWire); // Pass our oneWire reference to Dallas Temperature sensor

// DHT sensor setup
#define DHTTYPE DHT22      // DHT22 - DHT 22(AM2302)
const int DHT_PIN = 4;     // GPIO4 = D2 Digital pin connected to the DHT sensor
DHT dht(DHT_PIN, DHTTYPE); // Initialize DHT sensor

const int LOG_SIZE = 10;
String logs[LOG_SIZE];
int logIndex = 0;
int logCount = 0;

// Dodaje nowy wpis do logów (ring buffer)
void addLog(const String entry)
{
  logs[logIndex] = entry;
  logIndex = (logIndex + 1) % LOG_SIZE;
  if (logCount < LOG_SIZE)
    logCount++;
}

// Zwraca wszystkie logi jako jeden String (od najstarszego do najnowszego)
String getLogs()
{
  String result = "";
  int start = (logIndex + LOG_SIZE - logCount) % LOG_SIZE;
  for (int i = 0; i < logCount; i++)
  {
    int idx = (start + i) % LOG_SIZE;
    if (logs[idx].length() > 0)
    { // Pomija puste wpisy
      result += logs[idx] + "\n";
    }
  }
  return result;
}

void setup()
{
  Serial.begin(115200);
  delay(1000);

  if (!LittleFS.begin())
  {
    Serial.println("Błąd inicjalizacji LittleFS.");
    return;
  }
  Serial.println("System plików LittleFS gotowy.");

  Serial.println("Czekam 5 sekund na dowolny znak w Serial...");
  unsigned long startCzas = millis();
  while (millis() - startCzas < 5000)
  {
    if (Serial.available() > 0)
    {
      char c = Serial.read(); // Odbierz znak (choć treść nieistotna)
      Serial.println("Znak odebrany. Rozpoczynam konfigurację...");
      showMenu(); // Show the main menu
      configMode();
      break;
    }
  }
  readSettings();
  init_wifi();
  delay(500);
  init_oled();
  addLog("Device started");
  sendJson("Device started", 1, "log");

  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);
  pinMode(LED_PIN_4, OUTPUT);
  pinMode(LED_PIN_5, OUTPUT);

  sensors.begin(); // Initialize the DS18B20 sensor
  dht.begin();     // Initialize the DHT sensor
}

WebGui webGui;

void loop()
{
  WiFiClient client = server.available(); // Listen for incoming clients

  if (client)
  {
    Serial.println("\nNew Client."); // print a message out in the serial port
    String currentLine = "";         // make a String to hold incoming data from the client

    while (client.connected())
    { // loop while the client's connected
      if (client.available())
      {                         // if there's bytes to read from the client,
        char c = client.read(); // read a byte, then
        Serial.write(c);        // print it out the serial monitor
        header += c;
        if (c == '\n')
        { // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0)
          {
            if (header.indexOf("GET / HTTP/1.1") >= 0)
            {
              client.print(webGui.generator(webTableLCD, getLogs()));
              client.stop(); // Close the connection (1)
            }
            else if (header.indexOf("logs") >= 0)
            {
              client.print(getLogs());
              client.stop(); // Close the connection (2)
            }
            else if (header.indexOf("status") >= 0)
            {
              responseJson(client, "Connection ok", 1, "log", "Device Status");
              client.stop(); // Close the connection (2)
            }
            else if (header.indexOf("json") >= 0)
            {
              String jsonString = ""; // Zmienna do przechowywania odebranego JSON-a

              while (client.available())
              {
                char c = client.read();
                jsonString += c; // Dodaj odebrane dane do ciągu znaków
              }

              // Parsowanie odebranego JSON-a
              Serial.print(jsonString);
              StaticJsonDocument<400> jsonDoc; // Rozmiar dokumentu zależy od wielkości JSON-a

              // Parsowanie JSON
              DeserializationError error = deserializeJson(jsonDoc, jsonString);

              if (error)
              {
                Serial.print("Parsing JSON error: ");
                Serial.println(error.c_str());
                client.stop(); // Close the connection (3) - missing in original, should be added here to close on error
                return;
              }

              Serial.println("Parsing JSON...");

              for (JsonPair kv : jsonDoc.as<JsonObject>())
              {
                Serial.print(kv.key().c_str());
                Serial.print(": ");
                Serial.println(kv.value().as<String>());
              }
              if (!jsonDoc["requestID"].isNull())
              {
                addLog("Received requestID: " + jsonDoc["requestID"].as<String>());
              }
              else
              {
                addLog("No requestID in JSON (empyt or null)");
                jsonDoc["requestID"] = "Device request";
              }

              if (jsonDoc["function"] == "lcd") // Oled display fun
              {
                String value1 = jsonDoc["value1"].as<String>();
                String value2 = jsonDoc["value2"].as<String>();
                String value3 = jsonDoc["value3"].as<String>();
                String value4 = jsonDoc["value4"].as<String>();
                String value5 = jsonDoc["value5"].as<String>();
                String value6 = jsonDoc["value6"].as<String>();
                String value7 = jsonDoc["value7"].as<String>();
                String value8 = jsonDoc["value8"].as<String>();

                addLog("Received OLED data: " + value1 + ", " + value2 + ", " + value3 + ", " + value4 + ", " + value5 + ", " + value6 + ", " + value7 + ", " + value8);
                responseJson(client, "OLED updated", 1, "log", jsonDoc["requestID"].as<String>());
                handle_oled(value1, value2, value3, value4, value5, value6, value7, value8);
              }

              else if (jsonDoc["function"] == "builtinLed")
              {
                String ledState = jsonDoc["ledState"].as<String>();
                if (ledState == "on")
                {
                  digitalWrite(LED_PIN_1, HIGH);
                  addLog("builtinLed - ON");
                  responseJson(client, "builtinLed ON", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else if (ledState == "off")
                {
                  digitalWrite(LED_PIN_1, LOW);
                  addLog("builtinLed - OFF");
                  responseJson(client, "builtinLed OFF", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else
                {
                  addLog("Unknown LED state: " + ledState);
                  responseJson(client, "Unknown builtinLed state", 0, "error", jsonDoc["requestID"].as<String>());
                }
              }
              else if (jsonDoc["function"] == "led_pin_2")
              {
                String ledState = jsonDoc["ledState"].as<String>();
                if (ledState == "on")
                {
                  digitalWrite(LED_PIN_1, HIGH);
                  addLog("led_pin_2 - ON");
                  responseJson(client, "led_pin_2 ON", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else if (ledState == "off")
                {
                  digitalWrite(LED_PIN_1, LOW);
                  addLog("led_pin_2 - OFF");
                  responseJson(client, "led_pin_2 OFF", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else
                {
                  addLog("Unknown LED state: " + ledState);
                  responseJson(client, "Unknown led_pin_2 state", 0, "error", jsonDoc["requestID"].as<String>());
                }
              }
              else if (jsonDoc["function"] == "led_pin_3")
              {
                String ledState = jsonDoc["ledState"].as<String>();
                if (ledState == "on")
                {
                  digitalWrite(LED_PIN_2, HIGH);
                  addLog("led_pin_3 - ON");
                  responseJson(client, "led_pin_3 ON", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else if (ledState == "off")
                {
                  digitalWrite(LED_PIN_2, LOW);
                  addLog("led_pin_3 - OFF");
                  responseJson(client, "led_pin_3 OFF", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else
                {
                  addLog("Unknown LED state: " + ledState);
                  responseJson(client, "Unknown led_pin_3 state", 0, "error", jsonDoc["requestID"].as<String>());
                }
              }
              else if (jsonDoc["function"] == "led_pin_4")
              {
                String ledState = jsonDoc["ledState"].as<String>();
                if (ledState == "on")
                {
                  digitalWrite(LED_PIN_3, HIGH);
                  addLog("led_pin_4 - ON");
                  responseJson(client, "led_pin_4 ON", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else if (ledState == "off")
                {
                  digitalWrite(LED_PIN_3, LOW);
                  addLog("led_pin_4 - OFF");
                  responseJson(client, "led_pin_4 OFF", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else
                {
                  addLog("Unknown LED state: " + ledState);
                  responseJson(client, "Unknown led_pin_4 state", 0, "error", jsonDoc["requestID"].as<String>());
                }
              }
              else if (jsonDoc["function"] == "led_pin_5")
              {
                String ledState = jsonDoc["ledState"].as<String>();
                if (ledState == "on")
                {
                  digitalWrite(LED_PIN_5, HIGH);
                  addLog("led_pin_5 - ON");
                  responseJson(client, "led_pin_5 ON", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else if (ledState == "off")
                {
                  digitalWrite(LED_PIN_5, LOW);
                  addLog("led_pin_5 - OFF");
                  responseJson(client, "led_pin_5 OFF", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else
                {
                  addLog("Unknown LED state: " + ledState);
                  responseJson(client, "Unknown led_pin_5 state", 0, "error", jsonDoc["requestID"].as<String>());
                }
              }

              else if (jsonDoc["function"] == "getDHT22")
              {
                // float newT = random(20, 30); // Simulated temperature value
                // float newH = random(40, 60); // Simulated humidity value
                float newT = dht.readTemperature();
                float newH = dht.readHumidity();
                addLog("Simulated DHT22 data: Temperature = " + String(newT) + "°C, Humidity = " + String(newH) + "%");
                responseJson(client, "DHT22 data", 1, "log", jsonDoc["requestID"].as<String>());
                sendJson("DHT22 temperature: ", newT, "°C", jsonDoc["requestID"].as<String>());
                sendJson("DHT22 humidity: ", newH, "%", jsonDoc["requestID"].as<String>());
              }
              else if (jsonDoc["function"] == "getDS18B20")
              {
                sensors.requestTemperatures();
                float newT = sensors.getTempCByIndex(0);
                Serial.print("DS18B20 Temperature: ");
                Serial.println(newT);
                if (newT == DEVICE_DISCONNECTED_C)
                {
                  addLog("Error: DS18B20 sensor disconnected");
                  responseJson(client, "DS18B20 sensor disconnected", 0, "error", jsonDoc["requestID"].as<String>());
                }
                // float newT = random(20, 30); // Simulated temperature value
                addLog("Simulated DS18B20 data: Temperature = " + String(newT) + "°C");
                responseJson(client, "DS18B20 data", 1, "log", jsonDoc["requestID"].as<String>());
                sendJson("DS18B20 temperature: ", newT, "°C", jsonDoc["requestID"].as<String>());
              }
              else
              {
                addLog("Unknown function in JSON: " + jsonDoc["function"].as<String>());
                responseJson(client, "Unknown function", 0, "error", jsonDoc["requestID"].as<String>());
              }
              client.stop(); // Close the connection (4)
            }
            else
            {
              addLog("Unknown request");
              client.stop(); // Close the connection (5)
            }
            Serial.println("Client disconnected.");
            break;
          }
          else
          { // if you got a newline, then clear currentLine
            currentLine = "";
          }
        }
        else if (c != '\r')
        {                   // if you got anything else but a carriage return character,
          currentLine += c; // add it to the end of the currentLine
        }
      }
    }
    header = ""; // Clear the header variable
    delay(10);
    client.stop(); // Close the connection (7) -- this is a final safety, but may be redundant if already closed above
    Serial.println("Client disconnected.\n");
  }
  // Add a delay here to slow down requests and avoid error 104
  delay(1000); // 1 second delay between handling clients
}
