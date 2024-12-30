void init_oled() {
  display = new Adafruit_SSD1306(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

  // OLED used nonstandard SDA and SCL pins
  Wire.begin(D5, D6);
  
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display->begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    return;
  }
}

void handle_oled(String value1, String value2, String value3, String value4, String value5, String value6, String value7, String value8) {
  display->clearDisplay();
  display->setTextSize(1);
  display->setTextColor(SSD1306_WHITE);
  display->setCursor(0, 0);

  display->println(value1);
  display->println(value2);
  display->println(value3);
  display->println(value4);
  display->println(value5);
  display->println(value6);
  display->println(value7);
  display->println(value8);
  display->println(value8);

  display->display();
}
