#define button 7
#define volume A4
#define LED 13

bool prev_b = 0;
int prev_v = 0;
int scale = 100;

bool music_state = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(button, INPUT);
  pinMode(volume, INPUT);
  pinMode(LED, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  bool b = digitalRead(button);
  int v = analogRead(volume); // [0, 1023]

  if (prev_b != b && b){
    music_state = !music_state;
  }

  if (music_state){
    digitalWrite(LED, HIGH);
    delay(v/scale);
    digitalWrite(LED, LOW);
    delay((1023-v)/scale);
  } else{
    digitalWrite(LED, LOW);
  }
  
  if(prev_b != b && b){
    Serial.print("b\n");
  }
  prev_b = b;
  
  if(abs(prev_v - v) > 60){
    Serial.print("v\n");
    Serial.println(v);
    prev_v = v;
  }
  
  delay(10);
}
