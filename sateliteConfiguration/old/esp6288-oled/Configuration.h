const char* configFilePath = "/config.txt";

struct Config {
  String ssid;
  String password;
  String deviceIP;
  String deviceName;
  String deviceType;
  String serverAddress;
};

Config deviceConfig;

int inputStep = 0;  // Etap interaktywnego wprowadzania danych
bool isInputMode = false; // Czy użytkownik wprowadza dane

void saveConfig() {
  File file = LittleFS.open(configFilePath, "w");
  if (!file) {
    Serial.println("Nie udało się otworzyć pliku do zapisu.");
    return;
  }

  file.println(deviceConfig.ssid);
  file.println(deviceConfig.password);
  file.println(deviceConfig.deviceIP);
  file.println(deviceConfig.deviceName);
  file.println(deviceConfig.deviceType);
  file.println(deviceConfig.serverAddress);

  file.close();
  Serial.println("Plik konfiguracyjny zapisany.");
}

void readConfig() {
  if (!LittleFS.exists(configFilePath)) {
    Serial.println("Plik nie istnieje.");
    return;
  }
  File file = LittleFS.open(configFilePath, "r");
  if (!file) {
    Serial.println("Nie udało się otworzyć pliku do odczytu.");
    return;
  }
  Serial.println("Zawartość pliku:");
  while (file.available()) {
    String line = file.readStringUntil('\n');
    Serial.println(line);
  }
  file.close();
}

void readSettings() {
  File configFile = LittleFS.open(configFilePath, "r");
  if (!configFile) {
    Serial.println("Error opening file for reading!");
    return;
  }

  // Reading lines from a file
  deviceConfig.ssid = configFile.readStringUntil('\n');
  deviceConfig.ssid.trim();
  deviceConfig.password = configFile.readStringUntil('\n');
  deviceConfig.password.trim();
  deviceConfig.deviceIP = configFile.readStringUntil('\n');
  deviceConfig.deviceIP.trim();
  deviceConfig.deviceName = configFile.readStringUntil('\n');
  deviceConfig.deviceName.trim();
  deviceConfig.deviceType = configFile.readStringUntil('\n');
  deviceConfig.deviceType.trim();
  deviceConfig.serverAddress = configFile.readStringUntil('\n');
  deviceConfig.serverAddress.trim();

  configFile.close();

  // Display read data
  Serial.println("Ssid: " + deviceConfig.ssid);
  Serial.println("Password: " + deviceConfig.password);
  Serial.println("DeviceIP: " + deviceConfig.deviceIP);
  Serial.println("DeviceName: " + deviceConfig.deviceName);
  Serial.println("DeviceType: " + deviceConfig.deviceType);
  Serial.println("serverAddress: " + deviceConfig.serverAddress);
}

void deleteConfig() {
  if (LittleFS.remove(configFilePath)) {
    Serial.println("Plik usunięty.");
  } else {
    Serial.println("Nie udało się usunąć pliku.");
  }
}

void listFiles() {
  Serial.println("Lista plików:");
  Dir dir = LittleFS.openDir("/");
  while (dir.next()) {
    Serial.printf("  %s (%d bytes)\n", dir.fileName().c_str(), dir.fileSize());
  }
}

void showMenu() {
  Serial.println("\nWybierz opcję:");
  Serial.println("1 - Utwórz plik konfiguracyjny (domyślne dane)");
  Serial.println("2 - Usuń plik konfiguracyjny");
  Serial.println("3 - Odczytaj plik konfiguracyjny");
  Serial.println("4 - Lista plików");
  Serial.println("5 - Wprowadź dane ręcznie i zapisz plik");
  Serial.println("6 - Odczytaj plik konfiguracyjny v2");
  Serial.print("Wpisz numer i naciśnij Enter: ");
}

void handleUserInput(String input) {
  input.trim();

  switch (inputStep) {
    case 0:
      Serial.println("✍️ Wprowadź dane konfiguracyjne:");
      Serial.print("SSID: ");
      break;
    case 1:
      deviceConfig.ssid = input;
      Serial.print("Password: ");
      break;
    case 2:
      Serial.print("Device IP: ");
      deviceConfig.password = input;
      break;
    case 3:
      Serial.print("Device Name: ");
      deviceConfig.deviceIP = input;
      break;
    case 4:
      Serial.print("Device Type: ");
      deviceConfig.deviceName = input;
      break;
    case 5:
      Serial.print("Server Address: ");
      deviceConfig.deviceType = input;
      break;
    case 6:
      deviceConfig.serverAddress = input;
      Serial.println("✅ Dane wprowadzone. Zapisuję plik...");
      saveConfig();
      isInputMode = false;
      showMenu();
      inputStep = 0;
      return;
  }
  inputStep++;
}

void configMode() {
  while (true) {
    if (Serial.available()) {
      showMenu();
      String input = Serial.readStringUntil('\n');
      input.trim();
      Serial.println(input);
      Serial.println();

      if (isInputMode) {
        handleUserInput(input);
      }
      else {
        if (input == "1") {
          deviceConfig = {"ssidName", "ssidPass", "192.168.0.196", "deviceName", "LCD", "192.168.0.196"};
          saveConfig();
        } else if (input == "2") {
          deleteConfig();
        } else if (input == "3") {
          readConfig();
        } else if (input == "4") {
          listFiles();
        } else if (input == "5") {
          handleUserInput(input);
          isInputMode = true;
          return;
        } else if (input == "6") {
          readSettings();
        } else {
          Serial.println("Nieznana opcja.");
        }
      }
    }
  }
}


// WEB LAYOUT CONFIGURATION
String webTableLCD[31][4] = {
  { "hHtml", deviceConfig.deviceName , "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "formBegin", "/lcd", "LCD", "" },
  { "formText", "Text to send:", "value1", "1" },
  { "formText", "Text to send:", "value2", "1" },
  { "formText", "Text to send:", "value3", "1" },
  { "formText", "Text to send:", "value4", "1" },
  { "formText", "Text to send:", "value5", "1" },
  { "formText", "Text to send:", "value6", "1" },
  { "formText", "Text to send:", "value7", "1" },
  { "formText", "Text to send:", "value8", "1" },
  { "formEnd", "Send to LCD", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" }
};

String webTableSTD[31][4] = {
  { "hHtml", deviceConfig.deviceName , "", "" },
  { "pHtml", "Temp DHT22", "", "stC" },
  { "pHtml", "Humidity DHT22", "", "%" },
  { "pHtml", "Temp DS18B20", "", "stC" },
  { "", "", "", "" },
  { "formBegin", "/nawozy", "Nawozy", "" },
  { "formNumber", "Mikroelementy [s]:", "value1", "1" },
  { "formNumber", "Makroelementy [s]:", "value2", "1" },
  { "formNumber", "Carbo [s]:", "value3", "1" },
  { "formNumber", "Jack Daniels [s]:", "value4", "1" },
  { "formEnd", "Rozpocznij Dozowanie", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "button", "Gniazdo 1", "/socket1ON", "Send: ON" },
  { "button2", "Gniazdo 1", "/socket1OFF", "Send: 1 OFF" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "button", "Gniazdo 2", "/socket2ON", "Send: 2 ON" },
  { "button2", "Gniazdo 2", "/socket2OFF", "Send: 2 OFF" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "button", "Gniazdo 3", "/socket3ON", "Send: 3 ON" },
  { "button2", "Gniazdo 3", "/socket3OFF", "Send: 3 OFF" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "button", "GPIO All", "/gpioON", "All ON" },
  { "button2", "GPIO All", "/gpioOFF", "All OFF" }
};
