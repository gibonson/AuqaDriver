//  LAN CONFIGURATION

//wifi name and password
const char* ssid = "Monkey_town";
const char* password = "Avika666";

//device server settings
WiFiServer server(80);                 // Set web server port number to 80
IPAddress gateway(192, 168, 1, 1);     // Set your Gateway IP address
IPAddress subnet(255, 255, 0, 0);
IPAddress primaryDNS(8, 8, 8, 8);    //optional
IPAddress secondaryDNS(8, 8, 4, 4);  //optional


//  SERVER SETTINGS

//  test
//String serverName = "http://192.168.0.101:5000/api/addEvent";

//  production
String serverName = "http://192.168.0.110:5000/api/addEvent";


//  DEVICE SETTINGS

//  device 1
String deviceName = "Akwarium";
IPAddress local_IP(192, 168, 0, 184);

//  device 2
//String deviceName = "Korytarz";
//IPAddress local_IP(192, 168, 0, 185);

String webTable[31][4] = {
  { "hHtml", deviceName , "", "" },
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
