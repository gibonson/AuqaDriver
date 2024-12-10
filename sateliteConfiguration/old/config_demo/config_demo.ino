#include <FS.h>
#include <LittleFS.h>
const char *configFilePath = "/config.txt"; // Configuration path on device

#define CONFIG_TIMEOUT 5000  // Data waiting time

void setup() {
  delay(100);
  Serial.begin(9600);
  Serial.println("\nDevice starting - configuration...\n");
  // Initializing LittleFS
  if (!LittleFS.begin()) {
    Serial.println("LittleFS initialization error!");
    return;
  }

// Checking if the configuration file exists
if (LittleFS.exists(configFilePath)) {
    Serial.println("Loading configuration:");
    readSettings();
    Serial.println("\nIf you want to change something, type any character and press enter in the console...");
  } else {
    Serial.println("No settings saved. Starting configuration...");
    deviceConfiguration();
  }

  unsigned long startTime = millis();
  bool configMode = false;

  // Waiting for data for CONFIG_TIMEOUT/1000
  while (millis() - startTime < CONFIG_TIMEOUT) {
    if (Serial.available() > 0) {
      Serial.readStringUntil('\n');
      configMode = true;
      break; // go to config mode
    }
  }

  if (configMode) {
    Serial.println("Configuration Mode...");
    deviceConfiguration();
  } else {
    Serial.println("Device starting");
  }

}

void readSettings() {
  File configFile = LittleFS.open(configFilePath, "r");
  if (!configFile) {
    Serial.println("Error opening file for reading!");
    return;
  }

  // Reading lines from a file
  String ssid = configFile.readStringUntil('\n');
  ssid.trim();
  String password = configFile.readStringUntil('\n');
  password.trim();
  String deviceIP = configFile.readStringUntil('\n');
  deviceIP.trim();
  String deviceName = configFile.readStringUntil('\n');
  deviceName.trim();
  String deviceType = configFile.readStringUntil('\n');
  deviceType.trim();
  String serverIP = configFile.readStringUntil('\n');
  serverIP.trim();

  configFile.close();

  // Display read data
  Serial.println("Ssid: " + ssid);
  Serial.println("Password: " + password);
  Serial.println("DeviceIP: " + deviceIP);
  Serial.println("DeviceName: " + deviceName);
  Serial.println("DeviceType: " + deviceType);
  Serial.println("ServerIP: " + serverIP);
}

void saveSettings(String ssid, String password, String deviceIP, String deviceName, String deviceType, String serverIP) {
  File configFile = LittleFS.open(configFilePath, "w");
  if (!configFile) {
    Serial.println("Error opening file for writing!");
    return;
  }

  // Zapis danych w formacie tekstowym
  configFile.println(ssid);
  configFile.println(password);
  configFile.println(deviceIP);
  configFile.println(deviceName);
  configFile.println(deviceType);
  configFile.println(serverIP);
  configFile.close();
  Serial.println("Settings saved successfully.");
}

void deviceConfiguration() {
  String ssid, password, deviceIP, deviceName, deviceType, serverIP;

  Serial.println("Wifi ssid:");
  while (Serial.available() == 0); // Wait for data
  ssid = Serial.readStringUntil('\n');
  ssid.trim(); // Remove whitespace
  Serial.print("Received ssid: ");
  Serial.println(ssid);

  Serial.println("Set password:");
  while (Serial.available() == 0); // Wait for data
  password = Serial.readStringUntil('\n');
  password.trim(); // Remove whitespace
  Serial.print("Received password: ");
  Serial.println(password);

  Serial.println("Set deviceIP (xxx.xxx.xxx.xxx):");
  while (Serial.available() == 0); // Wait for data
  deviceIP = Serial.readStringUntil('\n');
  deviceIP.trim(); // Remove whitespace
  Serial.print("Received deviceIP: ");
  Serial.println(deviceIP);

  Serial.println("Set deviceName:");
  while (Serial.available() == 0);
  deviceName = Serial.readStringUntil('\n');
  deviceName.trim();
  Serial.print("Received deviceName: ");
  Serial.println(deviceName);

  Serial.println("Set deviceType:");
  while (Serial.available() == 0);
  deviceType = Serial.readStringUntil('\n');
  deviceType.trim();
  Serial.print("Received deviceType: ");
  Serial.println(deviceType);


  Serial.println("Set serverIP (http://192.168.0.101:5000/api/addEvent):");
  while (Serial.available() == 0);
  serverIP = Serial.readStringUntil('\n');
  serverIP.trim();
  Serial.print("Received serverIP: ");
  Serial.println(serverIP);

  Serial.println("Configuration completed...");
  saveSettings(ssid, password, deviceIP, deviceName, deviceType, serverIP);
}

void loop() {
  Serial.println("work");
  delay(10000);
}
