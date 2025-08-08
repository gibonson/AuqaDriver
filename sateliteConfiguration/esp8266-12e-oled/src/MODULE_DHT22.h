#include <DHT.h> // DHT sensor library

// DHT sensor setup
#define DHTTYPE DHT22      // DHT22 - DHT 22(AM2302)
const int DHT_PIN = 4;     // GPIO4 = D2 Digital pin connected to the DHT sensor
DHT dht(DHT_PIN, DHTTYPE); // Initialize DHT sensor

String webFormDHT22[3][4] = {{"formBegin", "", "form", ""},
                             {"formHidden", "", "function", "getDHT22"},
                             {"formEnd", "Get sensor value DHT22", "", ""}};

void init_dht22()
{
    addNewFormToWebGuiTable(webFormDHT22, sizeof(webFormDHT22) / sizeof(webFormDHT22[0]));
    dht.begin(); // Initialize the DHT sensor
}

void execute_dht22(StaticJsonDocument<400> jsonDoc)
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