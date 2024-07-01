class WebGui {
public:

  String noGui(String webContent[31][4]) {
    String html = htmlBegin();
    String endLine = "</br>\n";
    String sep = "<sep>";
    String sepEnd = "</sep>";
    for (int htmlLine = 0; htmlLine < 31; htmlLine++) {
      html = html + sep + webContent[htmlLine][0] + sepEnd + sep + webContent[htmlLine][1] + sepEnd + sep + webContent[htmlLine][2] + sepEnd + sep + webContent[htmlLine][3] + sepEnd + endLine;
      }
    html = html + "</body>\n";
    html = html + "<a href='javascript:history.back()'><button class='button'>Go Back</button></a>";
    return html;
  }




  String resultLogBegin (String deviceName) {
    String html = htmlBegin();
    String endLine = "</br>\n";
    String sep = "<sep>";
    String sepEnd = "</sep>";
    html = html + sep + "hHtml" + sepEnd + sep + deviceName + sepEnd + endLine;
    return html;
  }

  String resultLogContent (int value, String status) {
    String html = "";
    String endLine = "</br>\n";
    String sep = "<sep>";
    String sepEnd = "</sep>";
    html = html + sep + "pHtml" + sepEnd + sep + status + sepEnd + sep + value + sepEnd + sep + "Log" + sepEnd + endLine;
    return html;
  }
  
  String resultLogEnd () {
    String html = "";
    html = html + "</body>\n";
    html = html + "<a href='javascript:history.back()'><button class='button'>Go Back</button></a>";
    return html;
  }

  


  String generator(String webContent[31][4]) {
    String html = "";
    html = htmlBegin();
    for (int htmlLine = 0; htmlLine < 31; htmlLine++) {
      // Serial.println(webContent[htmlLine][0] + webContent[htmlLine][1] + webContent[htmlLine][2] + webContent[htmlLine][3]);
      if (webContent[htmlLine][0] == "hHtml") {
        html = html + hHtml(webContent[htmlLine][1]);
      } else if (webContent[htmlLine][0] == "pHtml") {
        html = html + pHtml(webContent[htmlLine][1] + " = ", webContent[htmlLine][2], webContent[htmlLine][3]);
      } else if (webContent[htmlLine][0] == "formBegin") {
        html = html + formBegin(webContent[htmlLine][1]);
      } else if (webContent[htmlLine][0] == "formText") {
        html = html + formText(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]);
      } else if (webContent[htmlLine][0] == "formNumber") {
        html = html + formNumber(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]);
      } else if (webContent[htmlLine][0] == "formEnd") {
        html = html + formEnd(webContent[htmlLine][1]);
      } else if (webContent[htmlLine][0] == "button") {
        html = html + htmlButton(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]);
      } else if (webContent[htmlLine][0] == "button2") {
        html = html + htmlButton2(webContent[htmlLine][1], webContent[htmlLine][2], webContent[htmlLine][3]);
      } else {
        html = html + htmlError();
      }
    }
    html = html + htmlEnd();
    return html;
  }

  String htmlBegin() {
    String html = "";
    html = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
          "<!DOCTYPE html><html><head><link rel='icon' href='data:,'>\n<style>\n"
          "html { font-family: Helvetica; font-size: 25px; text-align: center; background-color: #f2f2f2;}\n"
          "input[type=text], input[type=number] { font-size: 20px; width:100%; padding: 12px 20px; display: inline-block; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box}\n"
          ".submit, button { font-size: 20px; width: 100%; color: white; padding: 14px 20px; border: none; border-radius: 4px; cursor: pointer}\n"
          ".submit {background-color: #4CAF50;}\n"
          ".button {background-color: limegreen;}\n"
          ".button2 {background-color: tomato;}\n"
          "table {width: 80%;  margin: auto;}\n"
          "th, td {width: 50%; padding: 8px; text-align: left; border-bottom: 1px solid #ddd;}\n"
          "</style>\n</head>\n<body></br>\n";
    return html;
  }

  String hHtml(String text) {
    String html = "";
    html = "<h1>" + text + "</h1>\n";
    return html;
  }

  String pHtml(String text, String text2, String text3) {
    String html = "";
    html = "<p>" + text + text2 + text3 + "</p>\n";
    return html;
  }

  String formBegin(String action) {
    String html = "";
    html = "<form action='" + action + "'>\n<table>\n";
    return html;
  }

  String formText(String label, String name, String value) {
    String html = "";
    html = label + "<input type='text' name='" + name + "' value='" + value + "'></br>\n";
    return html;
  }

  String formNumber(String label, String name, String value) {
    String html = "";
    html = "<tr><td>" + label + "</td><td>" +"<input type='number' name='" + name + "' value='" + value + "'>" + "</td></tr>\n";
    return html;
  }

  String formEnd(String value) {
    String html = "";
    html = "<tr><td colspan='2'><input type = 'submit' class='submit' value = '" + value + "'></td></tr>\n</table>\n</form>\n";
    return html;
  }

  String htmlEnd() {
    String html = "";
    html = "</body>\n</html>\n";
    return html;
  }

  String htmlButton(String label, String name, String value) {
    String html = "";
    html = "<table><tr><td>" + label + "</td><td><a href='" + name + "'><button class='button'>" + value + "</button></a></table>\n";
    return html;
  }

  String htmlButton2(String label, String name, String value) {
    String html = "";
    html = "<table><tr><td>" + label + "</td><td><a href='" + name + "'><button class='button2'>" + value + "</button></a></table>\n";
    return html;
  }

  String htmlError() {
    String html = "";
    html = "</br>\n";
    return html;
  }
};
