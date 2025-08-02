#include <Arduino.h>
#include <LittleFS.h>    // ESP file system libraries, which store the Wi-Fi configuration file, device name, type and server address (json)
#include <ArduinoJson.h> // JSON library for Arduino, used to create and parse JSON objects

// #include <RCSwitch.h>           // RF remote control library to fix

// Project files
#include "logs.h" // Log management file
#include "Configuration.h"
#include "WifiOperation.h"
#include "JsonOperation.h"
#include "CONF_OLED.h"
#include "WebGui.h"
#include "CONF_DS18b20.h" // DS18B20 configuration file
#include "CONF_DTH22.h"   // DHT22 configuration file
#include "CONF_LED_PIN.h" // LED pin configuration file
String logBuffer = "";

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
  init_wifi(); // Initialize Wi-Fi connection

  delay(500);

  init_oled();     // Initialize OLED display
  init_led_pins(); // Initialize LED pins
  init_ds18b20();  // Initialize DS18B20 sensor configuration
  init_dht22();    // Initialize DHT22 sensor configuration
  
  addLog("Device started");
  sendJson("Device started", 1, "log");
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
                execute_oled(jsonDoc); // Execute OLED display function
              }
              else if (jsonDoc["function"] == "builtinLed")
              {
                execute_builtinLed(jsonDoc); // Execute built-in LED function
              }
              else if (jsonDoc["function"] == "led_pin_2")
              {
                execute_led_pin_2(jsonDoc); // Execute LED pin 3 function
              }
              else if (jsonDoc["function"] == "led_pin_3")
              {
                execute_led_pin_3(jsonDoc); // Execute LED pin 3 function
              }
              else if (jsonDoc["function"] == "led_pin_4")
              {
                execute_led_pin_4(jsonDoc); // Execute LED pin 5 function
              }
              else if (jsonDoc["function"] == "led_pin_5")
              {
                execute_led_pin_5(jsonDoc); // Execute LED pin 5 function
              }
              else if (jsonDoc["function"] == "getDHT22")
              {
                execute_dht22(jsonDoc); // Read DHT22 sensor data
              }
              else if (jsonDoc["function"] == "getDS18B20")
              {
                execute_ds18b20(jsonDoc); // Read DS18B20 sensor data
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
