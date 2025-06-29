#include <Arduino.h>
#include <LittleFS.h>    // ESP file system libraries, which store the Wi-Fi configuration file, device name, type and server address (json)
#include <ArduinoJson.h> // JSON library for Arduino, used to create and parse JSON objects

#include <DHT.h>                // DHT sensor library
#include <OneWire.h>            // OneWire library
//#include <RCSwitch.h>           // RF remote control library to fix
#include <DallasTemperature.h>  // DS18B20 Dallas Temperature library

// Project files
#include "Configuration.h"
#include "WifiOperation.h"
#include "JsonOperation.h"
#include "OledOperation.h"
#include "WebGui.h"
String logBuffer = "";

#define LED_PIN 2

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

  pinMode(LED_PIN, OUTPUT);
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
                jsonDoc["requestID"] = "manual request";
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
                  digitalWrite(LED_PIN, HIGH);
                  addLog("LED is ON");
                  responseJson(client, "LED ON", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else if (ledState == "off")
                {
                  digitalWrite(LED_PIN, LOW);
                  addLog("LED is OFF");
                  responseJson(client, "LED OFF", 1, "log", jsonDoc["requestID"].as<String>());
                }
                else
                {
                  addLog("Unknown LED state: " + ledState);
                  responseJson(client, "Unknown LED state", 0, "error", jsonDoc["requestID"].as<String>());
                }
              }
              else if (jsonDoc["function"] == "getDHT22")
              {
                float newT = random(20, 30); // Simulated temperature value
                float newH = random(40, 60); // Simulated humidity value
                addLog("Simulated DHT22 data: Temperature = " + String(newT) + "°C, Humidity = " + String(newH) + "%");
                sendJson("DHT22 temperature: ", newT, "°C", jsonDoc["requestID"].as<String>());
                sendJson("DHT22 humidity: ", newH, "%", jsonDoc["requestID"].as<String>());
                responseJson(client, "DHT22 data", 1, "log", jsonDoc["requestID"].as<String>());
              }
              else if (jsonDoc["function"] == "getDS18B20")
              {
                float newT = random(20, 30); // Simulated temperature value
                addLog("Simulated DS18B20 data: Temperature = " + String(newT) + "°C");
                sendJson("DS18B20 temperature: ", newT, "°C", jsonDoc["requestID"].as<String>());
                responseJson(client, "DS18B20 data", 1, "log", jsonDoc["requestID"].as<String>());
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
            // client.stop(); // Zamknij połączenie (6) -- this is redundant, already called above in all branches
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
    header = "";   // Clear the header variable
    delay(10);
    client.stop(); // Close the connection (7) -- this is a final safety, but may be redundant if already closed above
    Serial.println("Client disconnected.\n");
  }
}
