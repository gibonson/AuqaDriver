#include <OneWire.h>           // OneWire library
#include <DallasTemperature.h> // DS18B20 Dallas Temperature library

// DS18B20 sensor setup
const int ONE_WIRE_BUS = 16;         // GPIO16 = D0 pin connected to the  sensor
OneWire oneWire(ONE_WIRE_BUS);       // Setup a oneWire instance to communicate with any OneWire devices
DallasTemperature sensors(&oneWire); // Pass our oneWire reference to Dallas Temperature sensor

String webFormDS18B20[3][4] = {{"formBegin", "", "form", ""},
                               {"formHidden", "", "function", "getDS18B20"},
                               {"formEnd", "Get sensor value DS18B20", "", ""}};

void init_ds18b20()
{
    addNewFormToWebGuiTable(webFormDS18B20, sizeof(webFormDS18B20) / sizeof(webFormDS18B20[0]));
    sensors.begin(); // Initialize the DS18B20 sensor
}

void execute_ds18b20(StaticJsonDocument<400> jsonDoc)
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
    addLog("DS18B20 sensor data: Temperature = " + String(newT) + "°C");
    responseJson(client, "DS18B20 data", 1, "log", jsonDoc["requestID"].as<String>());
    sendJson("DS18B20 temperature: ", newT, "°C", jsonDoc["requestID"].as<String>());
}


