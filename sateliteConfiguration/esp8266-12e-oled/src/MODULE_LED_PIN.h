#pragma once

const int LED_PIN_1 = 2;  // GPIO2 = D4 = ESP LED - LED_PIN_1
const int LED_PIN_2 = 13; // GPIO13= D7 - Relay 1 control pin
const int LED_PIN_3 = 15; // GPIO15= D8 - Relay 2 control pin
const int LED_PIN_4 = 3;  // GPIO3= RX - Relay 3 control pin
const int LED_PIN_5 = 1;  // GPIO1 = TX - Relay 4 control pin

const int sequencePins[5] = {LED_PIN_1, LED_PIN_2, LED_PIN_3, LED_PIN_4, LED_PIN_5};
unsigned long sequenceDelays[5];
int currentLedStep = -1; // -1 oznacza, że sekwencja nie jest aktywna
unsigned long ledStepStartTime = 0;
String sequenceReqID = "";

String webFormBuiltinLed[49][4] = {{"pHtml", "webFormLed", "", ""},
                                   {"formBegin", "", "form", ""},
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

void execute_builtinLed(StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_1, HIGH);
    addLog("builtinLed - ON");
    responseJson("builtinLed ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_1, LOW);
    addLog("builtinLed - OFF");
    responseJson("builtinLed OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson("Unknown builtinLed state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_2(StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_2, HIGH);
    addLog("led_pin_2 - ON");
    responseJson("led_pin_2 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_2, LOW);
    addLog("led_pin_2 - OFF");
    responseJson("led_pin_2 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson("Unknown led_pin_2 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_3(StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_3, HIGH);
    addLog("led_pin_3 - ON");
    responseJson("led_pin_3 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_3, LOW);
    addLog("led_pin_3 - OFF");
    responseJson("led_pin_3 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson("Unknown led_pin_3 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_4(StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_4, HIGH);
    addLog("led_pin_4 - ON");
    responseJson("led_pin_4 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_4, LOW);
    addLog("led_pin_4 - OFF");
    responseJson("led_pin_4 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson("Unknown led_pin_4 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}

void execute_led_pin_5(StaticJsonDocument<400> jsonDoc)
{
  String ledState = jsonDoc["ledState"].as<String>();
  if (ledState == "on")
  {
    digitalWrite(LED_PIN_5, HIGH);
    addLog("led_pin_5 - ON");
    responseJson("led_pin_5 ON", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else if (ledState == "off")
  {
    digitalWrite(LED_PIN_5, LOW);
    addLog("led_pin_5 - OFF");
    responseJson("led_pin_5 OFF", 1, "log", jsonDoc["requestID"].as<String>());
  }
  else
  {
    addLog("Unknown LED state: " + ledState);
    responseJson("Unknown led_pin_5 state", 0, "error", jsonDoc["requestID"].as<String>());
  }
}


void execute_led_pin_all(StaticJsonDocument<400> jsonDoc)
{
  sequenceDelays[0] = jsonDoc["value1"].as<int>() * 1000;
  sequenceDelays[1] = jsonDoc["value2"].as<int>() * 1000;
  sequenceDelays[2] = jsonDoc["value3"].as<int>() * 1000;
  sequenceDelays[3] = jsonDoc["value4"].as<int>() * 1000;
  sequenceDelays[4] = jsonDoc["value5"].as<int>() * 1000;
  sequenceReqID = jsonDoc["requestID"].as<String>();

  // 2. Startujemy pierwszy krok sekwencji
  currentLedStep = 0;
  digitalWrite(sequencePins[0], HIGH);
  ledStepStartTime = millis(); // włączamy stoper
  
  addLog("led_pin_1 - ON");
  sendJson("led_pin_all started", 1, "log", sequenceReqID);

  // 3. OD RAZU odpowiadamy klientowi (brak blokowania)
  responseJson("led_pin_all started", 1, "log", sequenceReqID);
  client.stop(); 
}

// Ta funkcja będzie ciągle "nasłuchiwać" w głównej pętli
void handleLedSequence()
{
  // Jeśli sekwencja jest aktywna (kroki od 0 do 4)
  if (currentLedStep >= 0 && currentLedStep < 5)
  {
    // Jeśli upłynął czas dla obecnego pinu
    if (millis() - ledStepStartTime >= sequenceDelays[currentLedStep])
    {
      // Wyłącz obecny pin
      digitalWrite(sequencePins[currentLedStep], LOW);
      addLog("led_pin_" + String(currentLedStep + 1) + " - OFF");

      currentLedStep++; // Przejdź do następnego kroku

      // Jeśli to nie koniec, włącz następny pin
      if (currentLedStep < 5)
      {
        digitalWrite(sequencePins[currentLedStep], HIGH);
        addLog("led_pin_" + String(currentLedStep + 1) + " - ON");
        ledStepStartTime = millis(); // reset stopera
      }
      else
      {
        currentLedStep = -1; // Zakończ sekwencję
      }
    }
  }
}