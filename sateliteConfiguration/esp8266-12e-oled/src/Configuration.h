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
  input.trim(); // Remove leading/trailing whitespace

  if (input.isEmpty()) {
    Serial.println("❌ Wprowadzono pustą wartość. Spróbuj ponownie.");
    return; // Do not proceed if the input is empty
  }

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
      deviceConfig.password = input;
      Serial.print("Device IP: ");
      break;
    case 3:
      deviceConfig.deviceIP = input;
      Serial.print("Device Name: ");
      break;
    case 4:
      deviceConfig.deviceName = input;
      Serial.print("Device Type: ");
      break;
    case 5:
      deviceConfig.deviceType = input;
      Serial.print("Server Address: ");
      break;
    case 6:
      deviceConfig.serverAddress = input;
      Serial.println("✅ Dane wprowadzone. Zapisuję plik...");
      saveConfig(); // Save the configuration to the file
      isInputMode = false; // Exit input mode
      showMenu(); // Show the main menu
      inputStep = 0; // Reset the step counter
      return; // Exit the function
  }

  inputStep++; // Move to the next step
}

void configMode() {
  while (true) {
    if (Serial.available()) {
      String input = Serial.readStringUntil('\n'); // Odczytaj dane wejściowe do znaku końca linii
      input.trim(); // Usuń białe znaki na początku i końcu
      Serial.println(input); // Wyświetl dane wejściowe dla debugowania

      if (isInputMode) {
        handleUserInput(input); // Przetwarzaj dane wejściowe
      } else {
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
          isInputMode = true; // Wejdź w tryb wprowadzania danych
          Serial.println("Rozpoczynam wprowadzanie danych...");
          inputStep = 0; // Zresetuj licznik kroków
          Serial.print("SSID: "); // Poproś o pierwszy krok
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
  { "formBegin", "", "LCD", "" },
  { "formHidden", "", "function", "lcd"},
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
  { "formBegin", "", "LCD", "" },
  { "formHidden", "", "function", "builtinLed"},
  { "formHidden", "", "ledState", "on" },
  { "formEnd", "Led ON", "", "" },
  { "", "", "", "" },
  { "formBegin", "", "LCD", "" },
  { "formHidden", "", "function", "builtinLed"},
  { "formHidden", "", "ledState", "off" },
  { "formEnd", "Led OFF", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" },
  { "", "", "", "" }
};
