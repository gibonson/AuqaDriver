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
                            {"formEnd", "socket3OFF", "", ""}};

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

        mySwitch.enableTransmit(RC_TRANSMITER_PIN); // Transmitter is connected to Arduino Pin #0
        mySwitch.setProtocol(1);                    // Optional set protocol (default is 1, will work for most outlets)
        mySwitch.setPulseLength(350);               // Optional set pulse length.
                                                    // mySwitch.setRepeatTransmit(15);  // Optional set number of transmission repetitions.
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
            addLog("S433_1_ON");
            responseJson(client, "S433_1_ON", 1, "log", jsonDoc["requestID"].as<String>());
            mySwitch.send(4433, 24);

            sendJson("S433_1_ON", 1, "log", jsonDoc["requestID"].as<String>());
        }
        else if (String(jsonDoc["function"]).indexOf("socket1OFF") >= 0)
        {
            addLog("S433_1_OFF");
            responseJson(client, "S433_1_OFF", 1, "log", jsonDoc["requestID"].as<String>());
            mySwitch.send(4436, 24);

            sendJson("S433_1_OFF", 0, "log", jsonDoc["requestID"].as<String>());
        }

        if (String(jsonDoc["function"]).indexOf("socket2ON") >= 0)
        {
            addLog("S433_2_ON");
            responseJson(client, "S433_2_ON", 1, "log", jsonDoc["requestID"].as<String>());
            mySwitch.send(5201, 24);

            sendJson("S433_2_ON", 1, "log", jsonDoc["requestID"].as<String>());
        }
        else if (String(jsonDoc["function"]).indexOf("socket2OFF") >= 0)
        {
            addLog("S433_2_OFF");
            responseJson(client, "S433_2_OFF", 1, "log", jsonDoc["requestID"].as<String>());
            mySwitch.send(5204, 24);

            sendJson("S433_2_OFF", 0, "log", jsonDoc["requestID"].as<String>());
        }

        if (String(jsonDoc["function"]).indexOf("socket3ON") >= 0)
        {
            addLog("S433_3_ON");
            responseJson(client, "S433_3_ON", 1, "log", jsonDoc["requestID"].as<String>());
            mySwitch.send(5393, 24);

            sendJson("S433_3_ON", 1, "log", jsonDoc["requestID"].as<String>());
        }
        else if (String(jsonDoc["function"]).indexOf("socket3OFF") >= 0)
        {
            addLog("S433_3_OFF");
            responseJson(client, "S433_2_OFF", 1, "log", jsonDoc["requestID"].as<String>());
            mySwitch.send(5396, 24);

            sendJson("S433_3_OFF", 0, "log", jsonDoc["requestID"].as<String>());
        }
        else
        {
            addLog("Unknown 433 function in JSON: " + jsonDoc["function"].as<String>());
            responseJson(client, "Unknown 433 function", 0, "error", jsonDoc["requestID"].as<String>());
        }
        client.stop();
    }
}