// Wi-Fi and HTTP libraries
#include <ESP8266WiFi.h>        // Load Wi-Fi library
#include <ESP8266HTTPClient.h>  // HTTP client for ESP8266
//#include <HttpClient.h>         // HTTP client library

// Wi-Fi and HTTP configuration
#define CONFIG_TIMEOUT 5000  // Data waiting time
String header;                         // Variable to store the HTTP request
HTTPClient http;                       // HTTP client instance
WiFiClient client;                     // Wi-Fi client instance
String sthToSend = "";                 // Data to send over HTTP
unsigned long currentTime = millis();  // Current time
unsigned long previousTime = 0;        // Previous time
const long timeoutTime = 500;          // Timeout time in milliseconds

//Server configuration
WiFiServer server(80);                 // Set web server port number to 80
IPAddress gateway(192, 168, 1, 1);     // Set your Gateway IP address
IPAddress subnet(255, 255, 0, 0);
IPAddress primaryDNS(8, 8, 8, 8);    //optional
IPAddress secondaryDNS(8, 8, 4, 4);  //optional
IPAddress local_IP;

// IP address conversion from string to IPAddress, used in init_wifi.
bool convertStringToIP(String deviceIP, IPAddress& ip) {
  int parts[4] = {0};
  int partIndex = 0;

  // Rozdzielenie ciągu znaków na części na podstawie '.'
  char *token = strtok((char *)deviceIP.c_str(), ".");
  while (token != NULL && partIndex < 4) {
    parts[partIndex++] = atoi(token);
    token = strtok(NULL, ".");
  }

  // Sprawdzenie, czy mamy dokładnie 4 części
  if (partIndex != 4) {
    return false;
  }

  // Ustawienie adresu IP
  ip = IPAddress(parts[0], parts[1], parts[2], parts[3]);
  return true;
}

// to void setup
void init_wifi(){
  if (convertStringToIP(deviceConfig.deviceIP, local_IP)) {
    Serial.print("Skonwertowany IP: ");
    Serial.println(local_IP);
  } else {
    Serial.println("Błąd konwersji IP.");
  }
  
    if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  } else {
    Serial.println("Wifi configuration - OK");
  }
  
  Serial.println("Connecting to " + String(deviceConfig.ssid));
  WiFi.begin(deviceConfig.ssid, deviceConfig.password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("\nWiFi connected. IP address: "); // Print local IP address and start web server
  Serial.println(WiFi.localIP()); // Print local IP address and start web server
  Serial.println("");
  server.begin();
}
