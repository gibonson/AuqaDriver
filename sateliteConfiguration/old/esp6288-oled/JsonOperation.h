//Supports sending json to server address. Requires deviceConfig from Configuration.h file

void sendJson(String addInfo, int value, String type) {
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
