#define volume A4

void setup() {
  Serial.begin(9600);
  pinMode(volume, INPUT);
}

void loop() {
  int v = analogRead(volume);
  Serial.print("v\n");
  Serial.println(v);
  delay(10);
}
