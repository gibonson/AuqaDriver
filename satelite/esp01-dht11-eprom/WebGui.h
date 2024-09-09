extern String deviceName;
extern String logTable[31][4];


class WebGui {
  public:
    const String SEP_START = "<sep>";
    const String SEP_END = "</sep>";
    const String END_LINE = "</br>\n";
    const String HTML_BEGIN = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
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
    const String HTML_END = "</body>\n</html>\n";
    const String RESULT_LOG_END = "</body>\n<a href='javascript:history.back()'><button class='button'>Go Back</button></a>";
    const String HTML_ERROR = "</br>\n";


    String noGui(String webContent[31][4]) {
      String html = HTML_BEGIN + SEP_START + "hHtml" + SEP_END + SEP_START + deviceName + SEP_END + END_LINE;
      for (int htmlLine = 1; htmlLine < 31; htmlLine++) {
        html = html + SEP_START + webContent[htmlLine][0] + SEP_END + SEP_START + webContent[htmlLine][1] + SEP_END + SEP_START + webContent[htmlLine][2] + SEP_END + SEP_START + webContent[htmlLine][3] + SEP_END + END_LINE;
      }
      html = html + RESULT_LOG_END;
      for (int i = 0; i < 31; i++) {
        for (int j = 0; j < 4; j++) {
          logTable[i][j] = "";
        }
      }
      return html;
    }

    String resultLogBegin() {
      return HTML_BEGIN + SEP_START + "hHtml" + SEP_END + SEP_START + deviceName + SEP_END + END_LINE;
    }

    String resultLogContent(int value, String status) {
      return SEP_START + "pHtml" + SEP_END + SEP_START + status + SEP_END + SEP_START + value + SEP_END + SEP_START + "Log" + SEP_END + END_LINE;
    }

    String generator(String webContent[31][4]) {
      String html = "";
      html = HTML_BEGIN;
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
          html = html + HTML_ERROR;
        }
      }
      html = html + HTML_END;
      return html;
    }

    String hHtml(String text) {
      return "<h1>" + text + "</h1>\n";
    }

    String pHtml(String text, String text2, String text3) {
      return "<p>" + text + text2 + text3 + "</p>\n";
    }

    String formBegin(String action) {
      return "<form action='" + action + "'>\n<table>\n";
    }

    String formText(String label, String name, String value) {
      return "<tr><td>" + label + "</td><td><input type='text' name='" + name + "' value='" + value + "'></td></tr>\n";
    }

    String formNumber(String label, String name, String value) {
      return "<tr><td>" + label + "</td><td><input type='number' name='" + name + "' value='" + value + "'></td></tr>\n";
    }

    String formEnd(String value) {
      return "<tr><td colspan='2'><input type = 'submit' class='submit' value = '" + value + "'></td></tr>\n</table>\n</form>\n";
    }

    String htmlButton(String label, String name, String value) {
      return "<table><tr><td>" + label + "</td><td><a href='" + name + "'><button class='button'>" + value + "</button></a></table>\n";
    }

    String htmlButton2(String label, String name, String value) {
      return "<table><tr><td>" + label + "</td><td><a href='" + name + "'><button class='button2'>" + value + "</button></a></table>\n";
    }
};
