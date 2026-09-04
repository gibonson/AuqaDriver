#pragma once

// WEB LAYOUT CONFIGURATION
String webGuiTable[100][4];

void addNewFormToWebGuiTable(String newForm[][4], int newFormRows)
{
  int tableSize = sizeof(webGuiTable) / sizeof(webGuiTable[0]); // Calculate the size of the webGuiTable array

  int firstFree = 0;
  for (int i = 0; i < tableSize; i++)
  {
    // Serial.print("wiersz: " + String(i) + " ");

    if (webGuiTable[i][0] == "")
    {
      firstFree = i; // Find the first free row in the webGuiTable array
      break; // Exit the loop after finding the first free row
    }
  }

  // Copy 3 rows from newForm to webGuiTable starting at firstFree
  for (int k = 0; k < newFormRows; k++)
  {
    for (int m = 0; m < 4; m++)
    {
      webGuiTable[firstFree + k][m] = newForm[k][m]; // Fill the webGuiTable array with the newForm data
    }
  }
}

class WebGui
{
public:
  const String SEP_START = "<sep>";
  const String SEP_END = "</sep>";
  const String END_LINE = "</br>\n";
  const String HTML_BEGIN = "<!DOCTYPE html><html><head><link rel='icon' href='data:,'>\n<style>\n"
                            "html { font-family: Helvetica; font-size: 25px; text-align: center; background-color: #f2f2f2;}\n"
                            "input[type=text], input[type=number] { font-size: 20px; width:100%; padding: 12px 20px; display: inline-block; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box}\n"
                            ".submit, button { font-size: 20px; width: 100%; color: white; padding: 14px 20px; border: none; border-radius: 4px; cursor: pointer}\n"
                            ".submit {background-color: #4CAF50;}\n"
                            ".button {background-color: limegreen;}\n"
                            ".button2 {background-color: tomato;}\n"
                            "table {width: 80%;  margin: auto;}\n"
                            "th, td {width: 50%; padding: 8px; text-align: left; 1px solid #ddd;}\n"
                            ".button-row {display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;}\n"
                            "</style>\n</head>\n<body></br>\n"
                            "<div class='button-group button-row'>"
                            "<a href='/'><button class='button'>Home</button></a>"
                            "<a href='/newConfig'><button class='button'>NewConfig</button></a>"
                            "<a href='/readConfig'><button class='button'>Read Config</button></a>"
                            "<a href='/logs'><button class='button'>Logs</button></a>"
                            "<a href='/status'><button class='button'>Status</button></a>"
                            "<a href='/restart'><button class='button2'>restart</button></a>"
                            "</div>";
  const String HTML_END = "<script>"
                          "document.querySelectorAll('.json-form').forEach(form => {"
                          "form.addEventListener('submit', function(event) {"
                          "  event.preventDefault();"
                          "  const formData = new FormData(form);"
                          "  const jsonData = {};"
                          "  for (const [key, value] of formData.entries()) {"
                          "    jsonData[key] = value;"
                          "  }"
                          "  fetch('/json', {"
                          "    method: 'POST',"
                          "    headers: {"
                          "      'Content-Type': 'application/json'"
                          "    },"
                          "    body: JSON.stringify(jsonData)"
                          "  })"
                          "  .then(response => response.json())"
                          "  .then(data => {"
                          "    console.log('Sukces:', data);"
                          "    alert('JSON sent successfully!');"
                          "    refreshLogs();" // <-- Refresh logs after success
                          "  })"
                          "  .catch(error => {"
                          "    console.error('Błąd:', error);"
                          "    alert('Error sending JSON: ' + error.message);"
                          "    refreshLogs();" // <-- Refresh logs after error
                          "  });"
                          "});"
                          "});"
                          "function refreshLogs() {"
                          "  fetch('/logs')"
                          "    .then(response => response.text())"
                          "    .then(data => {"
                          "      document.getElementById('logs').value = data;"
                          "    })"
                          "    .catch(error => {"
                          "      console.error('Error fetching logs:', error);"
                          "    });"
                          "}"
                          "</script>"
                          "</body>\n</html>\n";
  const String RESULT_LOG_END = "</body>\n<a href='javascript:history.back()'><button class='button'>Go Back</button></a>";
  const String HTML_ERROR = "\n";

  void streamWebPage(String webContent[100][4], String logs = "no logs")
  {
    server.sendContent(HTML_BEGIN);
    server.sendContent("<h1>");
    server.sendContent(deviceConfig.deviceName);
    server.sendContent("</h1>");
    server.sendContent(END_LINE);

    server.sendContent("<div class='container'><textarea id='logs' readonly name='logs' rows='11' cols='80'>");
    server.sendContent(logs);
    server.sendContent("</textarea></br>\n</div>");

    for (int htmlLine = 0; htmlLine < 100; htmlLine++)
    {
      if (webContent[htmlLine][0] == "")
        continue; // Optymalizacja: pomijamy puste wiersze

      if (webContent[htmlLine][0] == "hHtml")
      {
        server.sendContent(hHtml(webContent[htmlLine][1]));
      }
      else if (webContent[htmlLine][0] == "pHtml")
      {
        server.sendContent(pHtml(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]));
      }
      else if (webContent[htmlLine][0] == "formBegin")
      {
        server.sendContent(formBegin(webContent[htmlLine][1]));
      }
      else if (webContent[htmlLine][0] == "formText")
      {
        server.sendContent(formText(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]));
      }
      else if (webContent[htmlLine][0] == "formNumber")
      {
        server.sendContent(formNumber(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]));
      }
      else if (webContent[htmlLine][0] == "formHidden")
      {
        server.sendContent(formHidden(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]));
      }
      else if (webContent[htmlLine][0] == "formEnd")
      {
        server.sendContent(formEnd(webContent[htmlLine][1]));
      }
      else if (webContent[htmlLine][0] == "button")
      {
        server.sendContent(htmlButton(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]));
      }
      else if (webContent[htmlLine][0] == "button2")
      {
        server.sendContent(htmlButton2(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]));
      }
      else
      {
        server.sendContent(HTML_ERROR);
      }
    }

    server.sendContent("<h6>APP Version: ");
    server.sendContent(String(APP_VERSION));
    server.sendContent("</h6>");
    server.sendContent(HTML_END);
  }

  String hHtml(String text)
  {
    return "<h1>" + text + "</h1>\n";
  }

  String pHtml(String text, String text2, String text3)
  {
    return "<h3>" + text + text2 + text3 + "</h3>\n";
  }

  String formBegin(String action)
  {
    // return "<form action='" + action + "'>\n<table>\n";
    return "<form class='json-form' action = json >\n<table>\n";
  }

  String formText(String label, String name, String value)
  {
    return "<tr><td>" + label + "</td><td><input type='text' name='" + name + "' value='" + value + "'></td></tr>\n";
  }

  String formNumber(String label, String name, String value)
  {
    return "<tr><td>" + label + "</td><td><input type='number' name='" + name + "' value='" + value + "'></td></tr>\n";
  }

  String formHidden(String label, String name, String value)
  {
    return "<input type='hidden' name='" + name + "' value='" + value + "'>\n";
  }

  String formEnd(String value)
  {
    return "<tr><td colspan='2'><input type = 'submit' class='submit' value = '" + value + "'></td></tr>\n</table>\n</form>\n";
  }

  String htmlButton(String label, String name, String value)
  {
    return "<table><tr><td>" + label + "</td><td><a href='" + name + "'><button class='button'>" + value + "</button></a></table>\n";
  }

  String htmlButton2(String label, String name, String value)
  {
    return "<table><tr><td>" + label + "</td><td><a href='" + name + "'><button class='button2'>" + value + "</button></a></table>\n";
  }

  String escapeHtml(String text)
  {
    text.replace("&", "&amp;");
    text.replace("<", "&lt;");
    text.replace(">", "&gt;");
    text.replace("\"", "&quot;");
    return text;
  }

  void streamNewConfigPage(String ssid, String password, String deviceIP, String deviceName, String serverAddress, String disableList)
  {
    String safeSSID = escapeHtml(ssid);
    String safePassword = escapeHtml(password);
    String safeDeviceIP = escapeHtml(deviceIP);
    String safeDeviceName = escapeHtml(deviceName);
    String safeServerAddress = escapeHtml(serverAddress);
    String safeDisableList = escapeHtml(disableList);
    safeDisableList.replace("\r", "");

    server.sendContent(HTML_BEGIN);
    server.sendContent("<h1>Device configuration</h1>");
    server.sendContent(END_LINE);
    server.sendContent("<div class='container'><form action='/saveNewConfig' method='POST'>\n");
    server.sendContent("<table>\n");

    server.sendContent("<tr><td>SSID</td><td><input type='text' name='ssid' value='" + safeSSID + "'></td></tr>\n");
    server.sendContent("<tr><td>Password</td><td><input type='text' name='password' value='" + safePassword + "'></td></tr>\n");
    server.sendContent("<tr><td>Device IP</td><td><input type='text' name='deviceIP' value='" + safeDeviceIP + "'></td></tr>\n");
    server.sendContent("<tr><td>Device Name</td><td><input type='text' name='deviceName' value='" + safeDeviceName + "'></td></tr>\n");
    server.sendContent("<tr><td>Server Address</td><td><input type='text' name='serverAddress' value='" + safeServerAddress + "'></td></tr>\n");
    server.sendContent("<tr><td>Disable list  </td><td><input type='text' name='disableList'   value='" + safeDisableList + "'></td></tr>\n");

    server.sendContent("<tr><td colspan='2'><input type='submit' class='submit' value='Save configuration'></td></tr>\n");
    server.sendContent("</table>\n</form></div>");
    server.sendContent(END_LINE);
    server.sendContent(HTML_END);
  }
};
