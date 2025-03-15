const int Light = 9;

void setup() {
  Serial.begin(9600);
  pinMode(Light, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    int number = wordToNumber(input);

    if (number > 0) {
      for (int i = 0; i < number; i++) {
        digitalWrite(Light, HIGH);
        delay(100);
        digitalWrite(Light, LOW);
        delay(100);
      }
    } else {
      digitalWrite(Light, LOW);
    }
  }
}

int wordToNumber(String word) {
  word.toLowerCase();  

  if (word == "one") return 1;
  if (word == "two") return 2;
  if (word == "three") return 3;
  if (word == "four") return 4;
  if (word == "five") return 5;
  if (word == "six") return 6;
  if (word == "seven") return 7;
  if (word == "eight") return 8;
  if (word == "nine") return 9;

  return 0;
}
