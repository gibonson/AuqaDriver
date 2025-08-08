const int LED_PIN_1 = 2;  // GPIO2 = D4 = ESP LED - LED_PIN_1
const int LED_PIN_2 = 12; // GPIO12= D6 - Relay 1 control pin
const int LED_PIN_3 = 13; // GPIO13= D7 - Relay 2 control pin
const int LED_PIN_4 = 15; // GPIO15= D8 - Relay 3 control pin
const int LED_PIN_5 = 3;  // GPIO5 = RX - Relay 4 control pin

String webFormBuiltinLed[8][4] = {{"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "builtinLed"},
                                  {"formHidden", "", "ledState", "on"},
                                  {"formEnd", "Led ON", "", ""},
                                  {"formBegin", "", "form", ""},
                                  {"formHidden", "", "function", "builtinLed"},
                                  {"formHidden", "", "ledState", "off"},
                                  {"formEnd", "Led OFF", "", ""}};

void init_led_pins()
{
  addNewFormToWebGuiTable(webFormBuiltinLed, sizeof(webFormBuiltinLed) / sizeof(webFormBuiltinLed[0]));
  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);
  pinMode(LED_PIN_4, OUTPUT);
  pinMode(LED_PIN_5, OUTPUT);
}

void execute_builtinLed(StaticJsonDocument<400> jsonDoc)
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

void execute_led_pin_2(StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_1, HIGH);
    addLog("led_pin_2 - ON");
    responseJson(client, "led_pin_2 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_1, LOW);
    addLog("led_pin_2 - OFF");
    responseJson(client, "led_pin_2 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson(client, "Unknown led_pin_2 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_3(StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_2, HIGH);
    addLog("led_pin_3 - ON");
    responseJson(client, "led_pin_3 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_2, LOW);
    addLog("led_pin_3 - OFF");
    responseJson(client, "led_pin_3 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson(client, "Unknown led_pin_3 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_4(StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_3, HIGH);
    addLog("led_pin_4 - ON");
    responseJson(client, "led_pin_4 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_3, LOW);
    addLog("led_pin_4 - OFF");
    responseJson(client, "led_pin_4 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson(client, "Unknown led_pin_4 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_5(StaticJsonDocument<400> jsonDoc)
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


