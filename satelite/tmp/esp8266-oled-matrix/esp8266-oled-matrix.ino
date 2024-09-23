#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define OLED_RESET     -1   // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C // If not work please try 0x3D
#define OLED_SDA D5         // Stock firmware shows wrong pins
#define OLED_SCL D6         // They swap SDA with SCL ;)

Adafruit_SSD1306 *display;

// Matrix effect parameters
const int numColumns = SCREEN_WIDTH / 6; // Assuming font width is 6
char matrix[numColumns]; // Array to store the current letters
int positions[numColumns]; // Current positions of falling characters
int trails[numColumns]; // Length of the trailing effect for each column
int transformations[numColumns]; // Index of the transformation set for each column

// Define transformation sets with up to 6 transformations each (with pixel size and empty spaces for fading out)
const int numTransformations = 10; // Number of transformation sets
const int maxStages = 6; // Max number of stages in each transformation set

// Struct for character data, including the character and its pixel size
struct CharTransform {
  char character;
  int pixelSize; // The approximate vertical size of the character in pixels
};

CharTransform transformationsSet[numTransformations][maxStages] = {
  { {'I', 8}, {'i', 6}, {'.', 2}, {' ', 0}, {' ', 0}, {' ', 0} },  // 'I' -> 'i' -> '.' -> nothing
  { {'T', 8}, {'t', 6}, {'+', 6}, {'.', 2}, {' ', 0}, {' ', 0} },  // 'T' -> 't' -> '+' -> '.'
  { {'H', 8}, {'h', 6}, {'|', 8}, {'.', 2}, {' ', 0}, {' ', 0} },  // 'H' -> 'h' -> '|' -> '.'
  { {'M', 8}, {'m', 6}, {'*', 6}, {'.', 2}, {' ', 0}, {' ', 0} },  // 'M' -> 'm' -> '*' -> '.'
  { {'O', 8}, {'o', 6}, {'0', 6}, {'.', 2}, {' ', 0}, {' ', 0} },  // 'O' -> 'o' -> '0' -> '.'
  { {'A', 8}, {'a', 6}, {'@', 6}, {'.', 2}, {' ', 0}, {' ', 0} },  // 'A' -> 'a' -> '@' -> '.'
  { {'E', 8}, {'e', 6}, {'3', 6}, {'.', 2}, {' ', 0}, {' ', 0} },  // 'E' -> 'e' -> '3' -> '.'
  { {'S', 8}, {'s', 6}, {'$', 6}, {'.', 2}, {' ', 0}, {' ', 0} },  // 'S' -> 's' -> '$' -> '.'
  { {'L', 8}, {'l', 6}, {'1', 6}, {'.', 2}, {' ', 0}, {' ', 0} },  // 'L' -> 'l' -> '1' -> '.'
  { {'Z', 8}, {'z', 6}, {'2', 6}, {'.', 2}, {' ', 0}, {' ', 0} }   // 'Z' -> 'z' -> '2' -> '.'
};

void init_oled() {
  display = new Adafruit_SSD1306(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

  // OLED used nonstandard SDA and SCL pins
  Wire.begin(D5, D6);
  
  if(!display->begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    return;
  }
  display->clearDisplay();
  display->display();
  
  // Initialize positions, letters and transformations for each column
  for (int i = 0; i < numColumns; i++) {
    positions[i] = random(0, SCREEN_HEIGHT / 8); // Random initial position
    transformations[i] = random(0, numTransformations); // Randomly pick a transformation set
    trails[i] = random(3, 6); // Random trail length (effect of fading)
  }
}

void updateMatrix() {
  display->clearDisplay();
  display->setTextSize(1);

  // Loop through each column
  for (int i = 0; i < numColumns; i++) {
    int transformationIndex = transformations[i]; // Get the transformation set for this column

    // Randomly generate a new starting character occasionally
    if (random(0, 10) > 8) {
      matrix[i] = transformationsSet[transformationIndex][0].character; // Start with the largest character
    }
    
    // Draw the character with a visual transition
    for (int j = 0; j < trails[i]; j++) {
      int pos = (positions[i] - j + SCREEN_HEIGHT / 8) % (SCREEN_HEIGHT / 8); // Position with wrap-around effect

      // Get the character and its pixel size for this stage
      CharTransform currentChar = transformationsSet[transformationIndex][min(j, maxStages-1)];
      
      if (currentChar.character != ' ') { // Only draw non-empty characters
        display->setTextColor(SSD1306_WHITE); // Set color to white (as it’s monochrome)
        display->setCursor(i * 6, pos * currentChar.pixelSize); // Adjust position based on pixel size
        display->print(currentChar.character);
      }
    }
    
    // Update the position of the column
    positions[i] = (positions[i] + 1) % (SCREEN_HEIGHT / 8);
  }
  
  display->display();
}

void setup() {
  Serial.begin(74880);
  init_oled();
}

void loop() {
  updateMatrix();
  delay(150); // Adjust speed of falling characters
}
