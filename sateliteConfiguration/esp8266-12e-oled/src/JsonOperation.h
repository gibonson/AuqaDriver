//Supports sending json to server address. Requires deviceConfig from Configuration.h file

void sendJson(String addInfo, int value, String type, String requestID = "")
{
  http.begin(client, deviceConfig.serverAddress);
  http.addHeader("Content-Type", "application/json");
  String jsonString = "{\"deviceIP\":\"" +
                      String(local_IP[0]) + "." +
                      String(local_IP[1]) + "." +
                      String(local_IP[2]) + "." +
                      String(local_IP[3]) +
                      "\",\"deviceName\":\"" + deviceConfig.deviceName +
                      "\",\"addInfo\":\"" + addInfo +
                      "\",\"type\":\"" + type +
                      "\",\"value\":" + String(value) + "}";
  Serial.println("Json to sent: " + jsonString);
  Serial.println(http.POST(jsonString));
}

void responseJson(WiFiClient &client, String addInfo, int value, String type, String requestID = "")
{
  StaticJsonDocument<200> jsonDoc;
  jsonDoc["requestID"] = requestID;
  jsonDoc["deviceIP"] = String(local_IP[0]) + "." + String(local_IP[1]) + "." + String(local_IP[2]) + "." + String(local_IP[3]);
  jsonDoc["deviceName"] = deviceConfig.deviceName;
  jsonDoc["addInfo"] = addInfo;
  jsonDoc["type"] = type;
  jsonDoc["value"] = value;

  // Serializacja JSON do ciągu znaków
  String jsonString;
  serializeJson(jsonDoc, jsonString);

  // Wyślij JSON do klienta
  client.print("HTTP/1.1 200 OK\r\n");
  client.print("Content-Type: application/json\r\n");
  client.print("Connection: close\r\n\r\n");
  client.print(jsonString);
}