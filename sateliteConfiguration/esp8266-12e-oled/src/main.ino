#include <Arduino.h>
#include <ArduinoJson.h> // JSON library for Arduino, used to create and parse JSON objects

// app version
#define APP_VERSION "0.0.1"

// Project files list
String moduleList = "DS18B20,DHT22,OLED,BuiltinLed,RADIO_433"; // List of modules available in the system

#include "BOARD_LOGGING.h"       // Log management file
#include "BOARD_CONFIGURATION.h" // Board configuration file
#include "BOARD_WIFI.h"          // Wi-Fi management file
#include "BOARD_JSON.h"
#include "BOARD_WEB_GUI.h" // Web GUI management file
#include "MODULE_OLED.h"
#include "MODULE_DS18B20.h"   // DS18B20 configuration file
#include "MODULE_DHT22.h"     // DHT22 configuration file
#include "MODULE_LED_PIN.h"   // LED pin configuration file
#include "MODULE_RADIO_433.h" // RF remote control configuration file

const int MOTION_SENSOR = 5; // GPIO5 = D1 - Motion Sensor

String urlDecode(const String &str)
{
  String result = "";
  for (unsigned int i = 0; i < str.length(); i++)
  {
    char c = str[i];
    if (c == '+')
    {
      result += ' ';
    }
    else if (c == '%' && i + 2 < str.length())
    {
      char hex[3] = {str[i + 1], str[i + 2], '\0'};
      result += (char)strtol(hex, NULL, 16);
      i += 2;
    }
    else
    {
      result += c;
    }
  }
  return result;
}

String getQueryValue(const String &query, const String &key)
{
  String prefix = key + "=";
  int start = query.indexOf(prefix);
  if (start < 0)
  {
    return "";
  }
  start += prefix.length();
  int end = query.indexOf('&', start);
  if (end < 0)
  {
    end = query.length();
  }
  return urlDecode(query.substring(start, end));
}

String getRequestLine(const String &headerText)
{
  int lineEnd = headerText.indexOf("\r\n");
  if (lineEnd < 0)
  {
    lineEnd = headerText.indexOf('\n');
  }
  if (lineEnd < 0)
  {
    return headerText;
  }
  return headerText.substring(0, lineEnd);
}

int getContentLength(const String &headerText)
{
  int start = headerText.indexOf("Content-Length:");
  if (start < 0)
  {
    start = headerText.indexOf("content-length:");
  }
  if (start < 0)
  {
    return 0;
  }
  int valueStart = headerText.indexOf(' ', start);
  if (valueStart < 0)
  {
    return 0;
  }
  int lineEnd = headerText.indexOf('\r', valueStart);
  if (lineEnd < 0)
  {
    lineEnd = headerText.indexOf('\n', valueStart);
  }
  if (lineEnd < 0)
  {
    lineEnd = headerText.length();
  }
  return headerText.substring(valueStart + 1, lineEnd).toInt();
}

// Checks if motion was detected
ICACHE_RAM_ATTR void detectsMovement()
{
  Serial.println("Interrupt!!!");
  sthToSend = "yes";
}

void setup()
{
  Serial.begin(115200);
  delay(1000);

  init_baord_file_system(); // Initialize the file system
  init_configuration();     // Initialize configuration settings
  readSettings();

  init_wifi(); // Initialize Wi-Fi connection
  delay(500);

  // here add all initialization functions
  init_oled();     // Initialize OLED display
  init_led_pins(); // Initialize LED pins
  init_ds18b20();  // Initialize DS18B20 sensor configuration
  init_dht22();    // Initialize DHT22 sensor configuration
  init_433();      // Initialize RF 433 module

  addLog("Device started");
  sendJson("Device started", 1, "log");

  pinMode(MOTION_SENSOR, INPUT_PULLUP);                                           // PIR Motion Sensor mode INPUT_PULLUP
  attachInterrupt(digitalPinToInterrupt(MOTION_SENSOR), detectsMovement, RISING); // Set motionSensor pin as interrupt, assign interrupt function and set RISING mode
}

WebGui webGui;

void loop()
{

  if (sthToSend == "yes")
  {
    Serial.println("zamiana");
    addLog("Motion detected");
    sendJson("Motion", 1, "Alert");
    sthToSend = "";
  }

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
              String page = webGui.generator(webGuiTable, getLogs());
              client.print(page); // wyślij całą stronę
              client.flush();     // upewnij się, że wszystko trafiło do TCP
              // delay(20);          // krótka pauza na wysłanie (można zmniejszyć)
              client.stop(); // Close the connection (1)
            }
            else if (header.indexOf("logs") >= 0)
            {
              client.print(getLogs());
              client.stop(); // Close the connection (2)
            }
            else if (header.indexOf("restart") >= 0)
            {
              responseJson(client, "Reset", 1, "log", "Device Status");
              client.stop();
              ESP.restart();
            }
            else if (header.indexOf("GET /newConfig") >= 0)
            {
              disableModuleList = readDisableList();
              String page = webGui.newConfigPage(deviceConfig.ssid, deviceConfig.password, deviceConfig.deviceIP, deviceConfig.deviceName, deviceConfig.serverAddress, disableModuleList);
              client.print(page);
              client.stop(); // Close the connection (2)
            }
            else if (header.indexOf("POST /saveNewConfig") >= 0)
            {
              int contentLength = getContentLength(header);
              String body = "";
              unsigned long now = millis();
              while ((int)body.length() < contentLength && millis() - now < 1000)
              {
                if (client.available())
                {
                  body += (char)client.read();
                }
              }

              String newSSID = getQueryValue(body, "ssid");
              String newPassword = getQueryValue(body, "password");
              String newDeviceIP = getQueryValue(body, "deviceIP");
              String newDeviceName = getQueryValue(body, "deviceName");
              String newServerAddress = getQueryValue(body, "serverAddress");
              String newDisableList = getQueryValue(body, "disableList");

              if (newSSID.length() > 0)
                deviceConfig.ssid = newSSID;
              if (newPassword.length() > 0)
                deviceConfig.password = newPassword;
              if (newDeviceIP.length() > 0)
                deviceConfig.deviceIP = newDeviceIP;
              if (newDeviceName.length() > 0)
                deviceConfig.deviceName = newDeviceName;
              if (newServerAddress.length() > 0)
                deviceConfig.serverAddress = newServerAddress;

              saveConfig();
              if (newDisableList.length() > 0)
              {
                saveDisableModuleList(newDisableList);
              }

              client.print("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n");
              client.print("<html><body><h1>Configuration updated</h1><p>Your settings were saved.</p><a href='/newConfig'><button class='button'>Back</button></a><a href='/'><button class='button'>Home</button></a></body></html>");
              client.stop();
            }
            else if (header.indexOf("disableModuleList") >= 0)
            {
              disableModuleList = readDisableList();
              client.println(disableModuleList);
              client.stop(); // Close the connection (2)
            }
            else if (header.indexOf("GET /saveDisableList?") >= 0)
            {
              int start = header.indexOf("GET /saveDisableList?");
              int end = header.indexOf(' ', start);
              String query = header.substring(start + strlen("GET /saveDisableList?"), end);
              String newContent = getQueryValue(query, "disableList");
              saveDisableModuleList(newContent);
              client.print("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n");
              client.print("<html><body><h1>Disable list updated</h1><a href='/disableModuleList'><button class='button'>Back</button></a><a href='/'><button class='button'>Home</button></a></body></html>");
              client.stop();
            }
            else if (header.indexOf("readConfig") >= 0)
            {
              String configData = "SSID: " + deviceConfig.ssid + "\n" +
                                  "Password: " + deviceConfig.password + "\n" +
                                  "Device IP: " + deviceConfig.deviceIP + "\n" +
                                  "Device Name: " + deviceConfig.deviceName + "\n" +
                                  "Server Address: " + deviceConfig.serverAddress;
              client.print(configData);
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

              // here add all functions to handle JSON requests
              if (jsonDoc["function"] == "lcd") // Oled display fun
              {
                execute_oled(client, jsonDoc); // Execute OLED display function
              }
              else if (jsonDoc["function"] == "builtinLed")
              {
                execute_builtinLed(client, jsonDoc); // Execute built-in LED function
              }
              else if (jsonDoc["function"] == "led_pin_2")
              {
                execute_led_pin_2(client, jsonDoc); // Execute LED pin 3 function
              }
              else if (jsonDoc["function"] == "led_pin_3")
              {
                execute_led_pin_3(client, jsonDoc); // Execute LED pin 3 function
              }
              else if (jsonDoc["function"] == "led_pin_4")
              {
                execute_led_pin_4(client, jsonDoc); // Execute LED pin 5 function
              }
              else if (jsonDoc["function"] == "led_pin_5")
              {
                execute_led_pin_5(client, jsonDoc); // Execute LED pin 5 function
              }
              else if (jsonDoc["function"] == "led_pin_all")
              {
                execute_led_pin_all(client, jsonDoc); // Execute LED pin all function
              }
              else if (jsonDoc["function"] == "getDHT22")
              {
                execute_dht22(client, jsonDoc); // Read DHT22 sensor data
              }
              else if (jsonDoc["function"] == "getDS18B20")
              {
                execute_ds18b20(client, jsonDoc); // Read DS18B20 sensor data
              }
              else if (String(jsonDoc["function"]).indexOf("433") >= 0)
              {
                execute_433(client, jsonDoc); // Execute 433 function
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
  delay(100); // 1 second delay between handling clients
}
