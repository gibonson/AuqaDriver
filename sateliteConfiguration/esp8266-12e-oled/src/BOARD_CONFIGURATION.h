const char *configFilePath = "/config.txt";
const char *disableModulePath = "/disableList.txt";
#include <LittleFS.h> // ESP file system libraries, which store the Wi-Fi configuration file, device name, type and server address (json)

void init_baord_file_system()
{
  if (!LittleFS.begin())
  {
    Serial.println("Błąd inicjalizacji LittleFS.");
    return;
  }
  Serial.println("System plików LittleFS gotowy.");
}

struct Config
{
  String ssid;
  String password;
  String deviceIP;
  String deviceName;
  String serverAddress;
};

Config deviceConfig;
String disableModuleList; // Lista modułów wyłączonych, oddzielonych przecinkami

int inputStep = 0;        // Etap interaktywnego wprowadzania danych
bool isInputMode = false; // Czy użytkownik wprowadza dane

void saveConfig()
{
  File file = LittleFS.open(configFilePath, "w");
  if (!file)
  {
    Serial.println("Nie udało się otworzyć pliku do zapisu.");
    return;
  }

  file.println(deviceConfig.ssid);
  file.println(deviceConfig.password);
  file.println(deviceConfig.deviceIP);
  file.println(deviceConfig.deviceName);
  file.println(deviceConfig.serverAddress);

  file.close();
  Serial.println("Plik konfiguracyjny zapisany.");
}

void saveDisableModuleList(String moduleList)
{
  File file = LittleFS.open(disableModulePath, "w");
  if (!file)
  {
    Serial.println("Nie udało się otworzyć pliku disableList.");
    return;
  }
  file.println(moduleList); // Zapisz zawartość disableModuleList do pliku
  file.close();
  Serial.println("Plik disableList zapisany.");
}

String readDisableList()
{
  if (!LittleFS.exists(disableModulePath))
  {
    Serial.println("Plik disableList nie istnieje.");
    return "";
  }
  File file = LittleFS.open(disableModulePath, "r");
  if (!file)
  {
    Serial.println("Nie udało się otworzyć pliku disableList do odczytu.");
    return "";
  }
  disableModuleList = file.readStringUntil('\n'); // Odczytaj zawartość pliku
  file.close();
  Serial.println("Zawartość pliku disableList:");
  Serial.println(disableModuleList); // Wyświetl zawartość pliku
  return disableModuleList; // Zwróć zawartość pliku
}

void readConfig()
{
  if (!LittleFS.exists(configFilePath))
  {
    Serial.println("Plik nie istnieje.");
    return;
  }
  File file = LittleFS.open(configFilePath, "r");
  if (!file)
  {
    Serial.println("Nie udało się otworzyć pliku do odczytu.");
    return;
  }
  Serial.println("Zawartość pliku:");
  while (file.available())
  {
    String line = file.readStringUntil('\n');
    Serial.println(line);
  }
  file.close();
}

void readSettings()
{
  File configFile = LittleFS.open(configFilePath, "r");
  if (!configFile)
  {
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
  deviceConfig.serverAddress = configFile.readStringUntil('\n');
  deviceConfig.serverAddress.trim();

  configFile.close();

  // Display read data
  Serial.println("Ssid: " + deviceConfig.ssid);
  Serial.println("Password: " + deviceConfig.password);
  Serial.println("DeviceIP: " + deviceConfig.deviceIP);
  Serial.println("DeviceName: " + deviceConfig.deviceName);
  Serial.println("serverAddress: " + deviceConfig.serverAddress);

  File disableFile = LittleFS.open(disableModulePath, "r");
  if (!disableFile)
  {
    Serial.println("Error opening disableList file for reading!");
    return; // Exit if the file cannot be opened
  }
  disableModuleList = disableFile.readString();
}

void deleteConfig()
{
  if (LittleFS.remove(configFilePath))
  {
    Serial.println("Plik usunięty.");
  }
  else
  {
    Serial.println("Nie udało się usunąć pliku.");
  }
}

void listFiles()
{
  Serial.println("Lista plików:");
  Dir dir = LittleFS.openDir("/");
  while (dir.next())
  {
    Serial.printf("  %s (%d bytes)\n", dir.fileName().c_str(), dir.fileSize());
  }
}


void handleUserInput(String input)
{
  input.trim(); // Remove leading/trailing whitespace

  if (input.isEmpty())
  {
    Serial.println("❌ Wprowadzono pustą wartość. Spróbuj ponownie.");
    return; // Do not proceed if the input is empty
  }

  switch (inputStep)
  {
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
    Serial.print("Server Address: ");
    break;
  case 5:
    deviceConfig.serverAddress = input;
    Serial.println("✅ Dane wprowadzone. Zapisuję plik...");
    saveConfig();        // Save the configuration to the file
    isInputMode = false; // Exit input mode
    inputStep = 0;       // Reset the step counter
    return;              // Exit the function
  }

  inputStep++; // Move to the next step
}


void configMode()
{
  while (true)
  {
    if (Serial.available())
    {
      String input = Serial.readStringUntil('\n'); // Odczytaj dane wejściowe do znaku końca linii
      input.trim();                                // Usuń białe znaki na początku i końcu
      Serial.println(input);                       // Wyświetl dane wejściowe dla debugowania

      if (isInputMode)
      {
        handleUserInput(input); // Przetwarzaj dane wejściowe
      }
      else
      {
        if (input == "1")
        {
          deviceConfig = {"SSID", "PASS", "192.168.0.197", "deviceName", "http://192.168.0.103:5000/api/addEvent"};
          saveConfig();
        }
        else if (input == "2")
        {
          deleteConfig();
        }
        else if (input == "3")
        {
          readConfig();
        }
        else if (input == "4")
        {
          listFiles();
        }
        else if (input == "5")
        {
          isInputMode = true; // Wejdź w tryb wprowadzania danych
          Serial.println("Rozpoczynam wprowadzanie danych...");
          inputStep = 0; // Zresetuj licznik kroków
        }
        else if (input == "6")
        {
          readSettings();
        }
        else if (input == "7")
        {
          saveDisableModuleList(moduleList); // Create or overwrite the disableList file
        }
        else if (input == "8")
        {
          readDisableList(); // Read the disableList file
        }
        else if (input == "9")
        {
          ESP.restart(); // Restart the ESP
        }
        else
        {
          Serial.println("Nieznana opcja.");
        }
      }
    }
  }
}

void init_configuration()
{
  Serial.println("Czekam 5 sekund na dowolny znak w Serial...");
  unsigned long startCzas = millis();
  while (millis() - startCzas < 5000)
  {
    if (Serial.available() > 0)
    {
      Serial.print(Serial.read()); // Odbierz znak (choć treść nieistotna)
      Serial.println("Znak odebrany. Rozpoczynam konfigurację...");
      Serial.println("\nWybierz opcję:");
      Serial.println("1 - Utwórz plik konfiguracyjny (domyślne dane)");
      Serial.println("2 - Usuń plik konfiguracyjny");
      Serial.println("3 - Odczytaj plik konfiguracyjny");
      Serial.println("4 - Lista plików");
      Serial.println("5 - Wprowadź dane ręcznie i zapisz plik");
      Serial.println("6 - Odczytaj plik konfiguracyjny v2");
      Serial.println("7 - Utwórz plik BlackList");
      Serial.println("8 - Odczytaj plik BlackList");
      Serial.println("9 - Restart ESP");
      Serial.print("Wpisz numer i naciśnij Enter: ");
      configMode();
      break;
    }
  }
}