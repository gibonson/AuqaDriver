#include <Arduino.h>
#include <LittleFS.h>    // ESP file system libraries, which store the Wi-Fi configuration file, device name, type and server address (json)
#include <ArduinoJson.h> // JSON library for Arduino, used to create and parse JSON objects

// Project files
#include "Configuration.h"
#include "WifiOperation.h"
#include "JsonOperation.h"
#include "OledOperation.h"
#include "WebGui.h"
String logs = "";

#define LED_PIN 2


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
  logs = "Device startted successfully.\n";
  sendJson("Device Start", 1, logs);

  pinMode(LED_PIN, OUTPUT);
}

void loop()
{
  WebGui webGui;
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
              client.print(webGui.generator(webTableLCD));
              client.stop(); // Close the connection
            }
            if (header.indexOf("json") >= 0)
            {
              String jsonString = ""; // Zmienna do przechowywania odebranego JSON-a

              while (client.available())
              {
                char c = client.read();
                jsonString += c; // Dodaj odebrane dane do ciągu znaków
              }

              // Parsowanie odebranego JSON-a
              Serial.print(jsonString);
              StaticJsonDocument<256> jsonDoc; // Rozmiar dokumentu zależy od wielkości JSON-a

              // Parsowanie JSON
              DeserializationError error = deserializeJson(jsonDoc, jsonString);

              if (error)
              {
                Serial.print("Błąd parsowania JSON: ");
                Serial.println(error.c_str());
                return;
              }

              Serial.println("Parsing JSON...");

              for (JsonPair kv : jsonDoc.as<JsonObject>())
              {
                Serial.print(kv.key().c_str());
                Serial.print(": ");
                Serial.println(kv.value().as<String>());
              }

              if (jsonDoc["function"] == "lcd")
              {
                String value1 = jsonDoc["value1"].as<String>();
                String value2 = jsonDoc["value2"].as<String>();
                String value3 = jsonDoc["value3"].as<String>();
                String value4 = jsonDoc["value4"].as<String>();
                String value5 = jsonDoc["value5"].as<String>();
                String value6 = jsonDoc["value6"].as<String>();
                String value7 = jsonDoc["value7"].as<String>();
                String value8 = jsonDoc["value8"].as<String>();

                handle_oled(value1, value2, value3, value4, value5, value6, value7, value8);
              }

              if (jsonDoc["function"] == "builtinLed")
              {
                String ledState = jsonDoc["ledState"].as<String>();
                if (ledState == "on")
                {
                  digitalWrite(LED_PIN, HIGH);
                  logs = "LED is ON";
                }
                else if (ledState == "off")
                {
                  digitalWrite(LED_PIN, LOW);
                  logs = "LED is OFF";
                }
                else
                {
                  logs = "Invalid LED state";
                }
              }
              responseJson(client, "addInfoTest", 0, "typeTest", "requestIDTest");
              client.stop(); // Zamknij połączenie
            }
            else
            {
              logs = "Page not Found";
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
    header = "";   // Clear the header variable
    client.stop(); // Close the connection
    Serial.println("Client disconnected.\n");
  }
}
