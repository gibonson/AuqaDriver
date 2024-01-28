#include <ESP8266WiFi.h>  // Load Wi-Fi library
#include "WebGui.h"

// 1	1361	1364
// 2	4433	4436
// 3	5201	5204
// 4	5393	5396

const char* ssid = "";
const char* password = "";
String deviceName = "Korytarz";
// IPAddress local_IP(192, 168, 0, 184);  // Set your Static IP address
IPAddress local_IP(192, 168, 0, 185);  // Set your Static IP address
WiFiServer server(80);                 // Set web server port number to 80
IPAddress gateway(192, 168, 1, 1);     // Set your Gateway IP address
IPAddress subnet(255, 255, 0, 0);
IPAddress primaryDNS(8, 8, 8, 8);    //optional
IPAddress secondaryDNS(8, 8, 4, 4);  //optional

String header;                         // Variable to store the HTTP request
unsigned long currentTime = millis();  // Current time
unsigned long previousTime = 0;        // Previous time
const long timeoutTime = 500;          // Define timeout time in milliseconds (example: 2000ms = 2s)

int LED1 = 2;  // Assign LED1 to pin GPIO2 - ESP LED
int LED2 = 14;
int LED3 = 12;
int LED4 = 13;
int LED5 = 15;

String webContent[31][4] = {
  { "hHtml", deviceName , "", "" },
  { "pHtml", "Temperatura", "", " stC" },
  { "pHtml", "Wilgotnosc", "", " %" },
  { "", "", "", "" },
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

#include <DHT.h>
#define DHTTYPE DHT22  // DHT22 - DHT 22(AM2302), DHT11 - DHT 11, DHT21 - DHT 21 (AM2301)
#define DHTPIN 4  // Digital pin connected to the DHT sensor
DHT dht(DHTPIN, DHTTYPE);
float t;
float h;

#include <RCSwitch.h>
RCSwitch mySwitch = RCSwitch();

void setup() {
  Serial.begin(9600);

  //ser led pin to output
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);
  pinMode(LED5, OUTPUT);
  
  // Transmitter is connected to Arduino Pin #0  
  mySwitch.enableTransmit(0); 
  // Optional set protocol (default is 1, will work for most outlets)
  mySwitch.setProtocol(1);
    // Optional set pulse length.
  mySwitch.setPulseLength(350);
  // Optional set number of transmission repetitions.
  // mySwitch.setRepeatTransmit(15);

  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  } else{
    Serial.println("CONF OK");
  }
  // Connect to Wi-Fi network with SSID and password
  Serial.print("Connecting to ");
  Serial.println(String(ssid));
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  // Print local IP address and start web server
  Serial.println("");
  Serial.println("WiFi connected. IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("");
  server.begin();

  delay(500);
  dht.begin();
  float newT = dht.readTemperature();
  float newH = dht.readHumidity();
  if (isnan(newT)) {
    Serial.println("Failed to read from DHT sensor!");
  }
}

void loop() {
  WebGui webGui;
  WiFiClient client = server.available();  // Listen for incoming clients

  if (client) {
    Serial.println();
    Serial.println("New Client.");  // print a message out in the serial port
    String currentLine = "";        // make a String to hold incoming data from the client

    while (client.connected()) {  // loop while the client's connected
      if (client.available()) {  // if there's bytes to read from the client,
        char c = client.read();  // read a byte, then
        Serial.write(c);         // print it out the serial monitor
        header += c;
        if (c == '\n') {  // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            Serial.println("HTTP / 1.1 200 OK"); // HTTP headers always start with a response code (e.g. HTTP/ 1.1 200 OK)
            Serial.println("Content - type: text / html"); // and a content-type so the client knows what's coming, then a blank line:
            Serial.println("Connection: close");
            // Serial.println(header);

            if (header.indexOf("GET / HTTP/1.1") >= 0) {
              float newT = dht.readTemperature();
              float newH = dht.readHumidity();
              webContent[1][2] = String(newT);
              webContent[2][2] = String(newH);
              client.print(webGui.generator(webContent));
            }
            else if (header.indexOf("noGui") >= 0) {
              float newT = dht.readTemperature();
              float newH = dht.readHumidity();
              webContent[1][2] = String(newT);
              webContent[2][2] = String(newH);
              client.print(webGui.noGui(webContent));
            }
            else if (header.indexOf("GET /nawozy") >= 0) {
              ///http://192.168.0.184/test1?name1=value1&name2=value2&name2=value2
              int start = header.indexOf(" ? ");
              int var1Start = header.indexOf("value1=");
              int var1Stop = header.indexOf("&", 0);
              int var2Start = header.indexOf("value2=");
              int var2Stop = header.indexOf("&", var1Stop + 1);
              int var3Start = header.indexOf("value3=");
              int var3Stop = header.indexOf("&", var2Stop + 1);
              int var4Start = header.indexOf("value4=");
              int var4Stop = header.indexOf(" HTTP/1.1");

              int value1 = header.substring(var1Start + 7, var1Stop).toInt();
              int value2 = header.substring(var2Start + 7, var2Stop).toInt();
              int value3 = header.substring(var3Start + 7, var3Stop).toInt();
              int value4 = header.substring(var4Start + 7, var4Stop).toInt();

              // Serial.println("Value1 position: " +  String(var1Start) + " - " +  String(var1Stop) + ", value1 = " +  String(value1));
              // Serial.println("Value2 position: " +  String(var2Start) + " - " +  String(var2Stop) + ", value2 = " +  String(value2));
              // Serial.println("Value3 position: " +  String(var3Start) + " - " +  String(var3Stop) + ", value3 = " +  String(value3));
              // Serial.println("Value4 position: " +  String(var4Start) + " - " +  String(var4Stop) + ", value4 = " +  String(value4));

              digitalWrite(LED2, HIGH);  // turn the LED on
              delay(value1 * 1000);
              digitalWrite(LED2, LOW);  // turn the LED off
              delay(100);

              digitalWrite(LED3, HIGH);  // turn the LED on
              delay(value2 * 1000);
              digitalWrite(LED3, LOW);  // turn the LED off
              delay(100);

              digitalWrite(LED4, HIGH);  // turn the LED on
              delay(value3 * 1000);
              digitalWrite(LED4, LOW);  // turn the LED off
              delay(100);

              digitalWrite(LED5, HIGH);  // turn the LED on
              delay(value4 * 1000);
              digitalWrite(LED5, LOW);  // turn the LED off
              delay(100);
              String value = String(value1) + String(value2) + String(value3) + String(value4);
              client.print(webGui.resultLog(value, "Nawozy", deviceName));
            }
            else if (header.indexOf("GET /gpioON") >= 0) {
              digitalWrite(LED1, HIGH);  // turn the LED on
              digitalWrite(LED2, HIGH);  // turn the LED on
              digitalWrite(LED3, HIGH);  // turn the LED on
              digitalWrite(LED4, HIGH);  // turn the LED on
              digitalWrite(LED5, HIGH);  // turn the LED on
              client.print(webGui.resultLog("12345", "All High", deviceName));
            }
            else if (header.indexOf("GET /gpioOFF") >= 0) {
              digitalWrite(LED1, LOW);  // turn the LED off
              digitalWrite(LED2, LOW);  // turn the LED off
              digitalWrite(LED3, LOW);  // turn the LED off
              digitalWrite(LED4, LOW);  // turn the LED off
              digitalWrite(LED5, LOW);  // turn the LED off
              client.print(webGui.resultLog("12345", "All Low", deviceName));
            } else if (header.indexOf("GET /socket1ON") >= 0) {
              mySwitch.send(4433, 24);
              client.print(webGui.resultLog("4433", "S1 On", deviceName));
            } else if (header.indexOf("GET /socket1OFF") >= 0) {
              mySwitch.send(4436, 24);
              client.print(webGui.resultLog("4436", "S1 Off", deviceName));
            } else if (header.indexOf("GET /socket2ON") >= 0) {
              mySwitch.send(5201, 24);
              client.print(webGui.resultLog("5201", "S2 On", deviceName));
            } else if (header.indexOf("GET /socket2OFF") >= 0) {
              mySwitch.send(5204, 24);
              client.print(webGui.resultLog("5204", "S2 Off", deviceName));
            } else if (header.indexOf("GET /socket3ON") >= 0) {
              mySwitch.send(5393, 24);
              client.print(webGui.resultLog("5393", "S3 On", deviceName));
            } else if (header.indexOf("GET /socket3OFF") >= 0) {
              mySwitch.send(5396, 24);
              client.print(webGui.resultLog("5396", "S3 Off", deviceName));
            } else {
              client.print(webGui.resultLog("0", "Not Found", deviceName));
            }
            break;
          } else {  // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    // Clear the header variable
    header = "";
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  }
}
