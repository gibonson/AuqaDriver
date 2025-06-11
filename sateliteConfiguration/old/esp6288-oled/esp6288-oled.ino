#include <Arduino.h>
#include <LittleFS.h> // ESP file system libraries, which store the Wi-Fi configuration file, device name, type and server address (json)

// Project files
#include "Configuration.h"
#include "WifiOperation.h"
#include "JsonOperation.h"
#include "OledOperation.h"
#include "WebGui.h"

void setup() {
  Serial.begin(115200);
  delay(1000);

  if (!LittleFS.begin()) {
    Serial.println("Błąd inicjalizacji LittleFS.");
    return;
  }
  Serial.println("System plików LittleFS gotowy.");

  Serial.println("Czekam 5 sekund na dowolny znak w Serial...");
  unsigned long startCzas = millis();
  while (millis() - startCzas < 5000) {
    if (Serial.available() > 0) {
      char c = Serial.read();  // Odbierz znak (choć treść nieistotna)
      Serial.println("Znak odebrany. Rozpoczynam konfigurację...");
      configMode();
      break;
    }
  }
  readSettings();
  init_wifi();
  delay(500);
  init_oled();
  sendJson("Device Start", 1, "Log");
}

void loop() {
  WebGui webGui;
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
              if (deviceConfig.deviceType == "LCD") {
                client.print(webGui.generator(webTableLCD));
              } else {
                client.print(webGui.generator(webTableSTD));
              }
              client.stop();    // Close the connection
            }
            else if (header.indexOf("noGui") >= 0) {
              if (deviceConfig.deviceType == "LCD") {
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


              value1 = "IP:" + String(local_IP[0]) + "." + String(local_IP[1]) + "." + String(local_IP[2]) + "." + String(local_IP[3]);
              value2 = WiFi.status();
              //    WL_IDLE_STATUS      = 0,
              //    WL_NO_SSID_AVAIL    = 1,
              //    WL_SCAN_COMPLETED   = 2,
              //    WL_CONNECTED        = 3,
              //    WL_CONNECT_FAILED   = 4,
              //    WL_CONNECTION_LOST  = 5,
              //    WL_DISCONNECTED     = 6

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



              handle_oled(value1, value2, value3, value4, value5, value6 , value7 , value8);
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
