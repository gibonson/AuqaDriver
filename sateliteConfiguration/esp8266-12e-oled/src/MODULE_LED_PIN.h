const int LED_PIN_1 = 2;  // GPIO2 = D4 = ESP LED - LED_PIN_1
const int LED_PIN_2 = 13; // GPIO13= D7 - Relay 1 control pin
const int LED_PIN_3 = 15; // GPIO15= D8 - Relay 2 control pin
const int LED_PIN_4 = 3;  // GPIO3= RX - Relay 3 control pin
const int LED_PIN_5 = 1;  // GPIO1 = TX - Relay 4 control pin

String webFormBuiltinLed[48][4] = {{"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "builtinLed"},
                                  {"formHidden", "", "ledState", "on"},
                                  {"formEnd", "Led ON", "", ""},
                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "builtinLed"},
                                  {"formHidden", "", "ledState", "off"},
                                  {"formEnd", "Led OFF", "", ""},

                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_2"},
                                  {"formHidden", "", "ledState", "on"},
                                  {"formEnd", "Led 2", "", ""},
                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_2"},
                                  {"formHidden", "", "ledState", "off"},
                                  {"formEnd", "Led 2", "", ""},

                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_3"},
                                  {"formHidden", "", "ledState", "on"},
                                  {"formEnd", "Led 3", "", ""},
                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_3"},
                                  {"formHidden", "", "ledState", "off"},
                                  {"formEnd", "Led 3", "", ""},

                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_4"},
                                  {"formHidden", "", "ledState", "on"},
                                  {"formEnd", "Led 4", "", ""},
                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_4"},
                                  {"formHidden", "", "ledState", "off"},
                                  {"formEnd", "Led 4", "", ""},

                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_5"},
                                  {"formHidden", "", "ledState", "on"},
                                  {"formEnd", "Led 5", "", ""},
                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_5"},
                                  {"formHidden", "", "ledState", "off"},
                                  {"formEnd", "Led 5", "", ""},

                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "led_pin_all"},
                                  {"formText", "builtinLed", "value1", "1"},
                                  {"formText", "led_pin_2", "value2", "1"},
                                  {"formText", "led_pin_3", "value3", "1"},
                                  {"formText", "led_pin_4", "value4", "1"},
                                  {"formText", "led_pin_5", "value5", "1"},
                                  {"formEnd", "Start timer", "", ""}};


void init_led_pins()
{
  addNewFormToWebGuiTable(webFormBuiltinLed, sizeof(webFormBuiltinLed) / sizeof(webFormBuiltinLed[0]));
  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);
  pinMode(LED_PIN_4, OUTPUT);
  pinMode(LED_PIN_5, OUTPUT);
}

void execute_builtinLed(WiFiClient &client, StaticJsonDocument<400> jsonDoc)
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

void execute_led_pin_2(WiFiClient &client, StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_2, HIGH);
    addLog("led_pin_2 - ON");
    responseJson(client, "led_pin_2 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_2, LOW);
    addLog("led_pin_2 - OFF");
    responseJson(client, "led_pin_2 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson(client, "Unknown led_pin_2 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_3(WiFiClient &client, StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_3, HIGH);
    addLog("led_pin_3 - ON");
    responseJson(client, "led_pin_3 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_3, LOW);
    addLog("led_pin_3 - OFF");
    responseJson(client, "led_pin_3 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson(client, "Unknown led_pin_3 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_4(WiFiClient &client, StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_4, HIGH);
    addLog("led_pin_4 - ON");
    responseJson(client, "led_pin_4 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_4, LOW);
    addLog("led_pin_4 - OFF");
    responseJson(client, "led_pin_4 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson(client, "Unknown led_pin_4 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_5(WiFiClient &client, StaticJsonDocument<400> jsonDoc)
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


void execute_led_pin_all(WiFiClient &client, StaticJsonDocument<400> jsonDoc)
{
  int value1 = jsonDoc["value1"];
  int value2 = jsonDoc["value2"];
  int value3 = jsonDoc["value3"];
  int value4 = jsonDoc["value4"];
  int value5 = jsonDoc["value5"];

Serial.println("value1: " + String(value1));
Serial.println("value2: " + String(value2));
Serial.println("value3: " + String(value3));
Serial.println("value4: " + String(value4));
Serial.println("value5: " + String(value5));

    responseJson(client, "led_pin_all", 1, "log", jsonDoc["requestID"].as<String>());
    sendJson("led_pin_all", 1, "log", jsonDoc["requestID"].as<String>());


    digitalWrite(LED_PIN_1, HIGH);
    addLog("led_pin_1 - ON");
    sendJson("led_pin_1_on", value5, "log", jsonDoc["requestID"].as<String>());
    delay(value1 * 1000);
    digitalWrite(LED_PIN_1, LOW);
    addLog("led_pin_1 - OFF");
    sendJson("led_pin_1_off", value1, "log", jsonDoc["requestID"].as<String>());

    digitalWrite(LED_PIN_2, HIGH);
    addLog("led_pin_2 - ON");
    sendJson("led_pin_2_on", value5, "log", jsonDoc["requestID"].as<String>());
    delay(value2 * 1000);
    digitalWrite(LED_PIN_2, LOW);
    addLog("led_pin_2 - OFF");
    sendJson("led_pin_2_off", value2, "log", jsonDoc["requestID"].as<String>());

    digitalWrite(LED_PIN_3, HIGH);
    addLog("led_pin_3 - ON");
    sendJson("led_pin_3_on", value5, "log", jsonDoc["requestID"].as<String>());
    delay(value3 * 1000);
    digitalWrite(LED_PIN_3, LOW);
    addLog("led_pin_3 - OFF");
    sendJson("led_pin_3_off", value3, "log", jsonDoc["requestID"].as<String>());

    digitalWrite(LED_PIN_4, HIGH);
    addLog("led_pin_4 - ON");
    sendJson("led_pin_4_on", value5, "log", jsonDoc["requestID"].as<String>());
    delay(value4 * 1000);
    digitalWrite(LED_PIN_4, LOW);
    addLog("led_pin_4 - OFF");
    sendJson("led_pin_4_off", value5, "log", jsonDoc["requestID"].as<String>());

    digitalWrite(LED_PIN_5, HIGH);
    addLog("led_pin_5 - ON");
    sendJson("led_pin_5_on", value5, "log", jsonDoc["requestID"].as<String>());
    delay(value5 * 1000);
    digitalWrite(LED_PIN_5, LOW);
    addLog("led_pin_5 - OFF");
    sendJson("led_pin_5_off", value5, "log", jsonDoc["requestID"].as<String>());

}