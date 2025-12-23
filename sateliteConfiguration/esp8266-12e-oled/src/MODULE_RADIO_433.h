#include "RCSwitch.h"

// RF 433 remote control setup
RCSwitch mySwitch = RCSwitch();  // Initialize RF switch
const int RC_TRANSMITER_PIN = 0; // GPIO0 = D3 Transmitter data pin

String webForm433[18][4] = {{"formBegin", "", "form", ""},
                            {"formHidden", "", "function", "433socket1ON"},
                            {"formEnd", "socket1ON", "", ""},
                            {"formBegin", "", "form", ""},
                            {"formHidden", "", "function", "433socket1OFF"},
                            {"formEnd", "socket1OFF", "", ""},
                            {"formBegin", "", "form", ""},
                            {"formHidden", "", "function", "433socket2ON"},
                            {"formEnd", "socket2ON", "", ""},
                            {"formBegin", "", "form", ""},
                            {"formHidden", "", "function", "433socket2OFF"},
                            {"formEnd", "socket2OFF", "", ""},
                            {"formBegin", "", "form", ""},
                            {"formHidden", "", "function", "433socket3ON"},
                            {"formEnd", "socket3ON", "", ""},
                            {"formBegin", "", "form", ""},
                            {"formHidden", "", "function", "433socket3OFF"},
                            {"formEnd", "socket3OFF", "", "",
                            }};

void init_433()
{
    String moduleName = "433";
    Serial.println(disableModuleList);
    if (disableModuleList.indexOf(moduleName) != -1)
    {
        Serial.println("Module " + moduleName + " is disabled.");
    }
    else
    {
        Serial.println("Initializing module: " + moduleName);
        addNewFormToWebGuiTable(webForm433, sizeof(webForm433) / sizeof(webForm433[0]));
        // RF 433 remote control setup
        RCSwitch mySwitch = RCSwitch();  // Initialize RF switch
        const int RC_TRANSMITER_PIN = 0; // GPIO0 = D3 Transmitter data pin
    }
}

void execute_433(WiFiClient &client, StaticJsonDocument<400> jsonDoc)
{
    String moduleName = "433";
    if (disableModuleList.indexOf(moduleName) != -1)
    {
        addLog("Module " + moduleName + " is disabled in disableModuleList");
        responseJson(client, "Module " + moduleName + " is disabled in disableModuleList", 0, "error", jsonDoc["requestID"].as<String>());
    }
    else
    {
        if (String(jsonDoc["function"]).indexOf("socket1ON") >= 0)
        {
            addLog("Socket_1_ON");
            responseJson(client, "Socket_1_ON", 1, "log", jsonDoc["requestID"].as<String>());
            sendJson("Socket_1_ON", 1, "log", jsonDoc["requestID"].as<String>());
            mySwitch.send(4433, 24);
        }
        else if (String(jsonDoc["function"]).indexOf("socket1OFF") >= 0)
        {
            addLog("Socket_1_OFF");
            responseJson(client, "Socket_1_OFF", 1, "log", jsonDoc["requestID"].as<String>());
            sendJson("Socket_1_OFF", 0, "log", jsonDoc["requestID"].as<String>());
            mySwitch.send(4436, 24);
        }
        
        

            //         else if (header.indexOf("GET /socket1ON") >= 0) {
            //   mySwitch.send(4433, 24);
            //   resultHtml += webGui.resultLogContent(1, "S1 - stan");
            // }
            // else if (header.indexOf("GET /socket1OFF") >= 0) {
            //   mySwitch.send(4436, 24);
            //   resultHtml += webGui.resultLogContent(0, "S1 - stan");
            // } else if (header.indexOf("GET /socket2ON") >= 0) {
            //   mySwitch.send(5201, 24);
            //   resultHtml += webGui.resultLogContent(1, "S2 - stan");
            // }
            // else if (header.indexOf("GET /socket2OFF") >= 0) {
            //   mySwitch.send(5204, 24);
            //   resultHtml += webGui.resultLogContent(0, "S2 - stan");
            // }
            // else if (header.indexOf("GET /socket3ON") >= 0) {
            //   mySwitch.send(5393, 24);
            //   resultHtml += webGui.resultLogContent(1, "S3 - stan");
            // }
            // else if (header.indexOf("GET /socket3OFF") >= 0) {
            //   mySwitch.send(5396, 24);
            //   resultHtml += webGui.resultLogContent(0, "S3 - stan");
            // }
        // addLog("Simulated DHT22 data: Temperature = " + String(666) + "°C, Humidity = " + String(666) + "%");
        // responseJson(client, "DHT22 data", 1, "log", jsonDoc["requestID"].as<String>());
        // sendJson("DHT22 humidity: ", 666, "%", jsonDoc["requestID"].as<String>());
        client.stop();
    }
}