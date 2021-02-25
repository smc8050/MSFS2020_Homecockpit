#include "cockpit_io.h"
#include "MultiplexedRotaryEncoder.h"


//**************************************************************************
//*********************************Definitions******************************
//**************************************************************************


//Mux control pins
int s0 = 22;
int s1 = 23;
int s2 = 24;
int s3 = 25;

// Divers. Variables:
int buttonState;             // the current reading from the input pin
int lastButtonState = HIGH;   // the previous reading from the input pin
int lastMux;
int lastChannel;
unsigned long lastPressed;

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 50;    // the debounce time; increase if the output flickers
unsigned long repressDelay = 500;    // thge time after which the butten can be repressed

//Setting up multiplexed encoder objects
// Get the total ammount of encoders
int encoder_count = sizeof(encoderlist) / sizeof(encoderlist[0]);
// allocating dynamic array
// of Size encoder_count using malloc()
RotaryEncoder* encoder_arr = (RotaryEncoder*)malloc(sizeof(RotaryEncoder) * encoder_count);

//Set Speed threshhold for fast/slow rotation
int Speed_Threshhold = 100;

//**************************************************************************
//*********************************Setup************************************
//**************************************************************************

void setup() {
  //Setup Multiplexer pins
  pinMode(s0, OUTPUT);
  pinMode(s1, OUTPUT);
  pinMode(s2, OUTPUT);
  pinMode(s3, OUTPUT);
  digitalWrite(s0, LOW);
  digitalWrite(s1, LOW);
  digitalWrite(s2, LOW);
  digitalWrite(s3, LOW);

  //Set Signal Pins from all multiplexers (Pins 38-52) to input pullup
  for (int i = 38; i < 52; i ++) {
    pinMode(i, INPUT_PULLUP);
  }

  // Set All Relais Pins to Output mode
  int rows =  sizeof relaislist / sizeof relaislist[0];
  for (int k = 0; k < rows; k ++) {
    digitalWrite(relaislist[k][2], HIGH);//turn off all Relais
    pinMode(relaislist[k][2], OUTPUT);
  }


  //Define Setup for multiplexers -> could be done via seperate header
  //int encoder_setup[2][4] = {{41, 41, 0, 1}, {41, 41, 3, 4}};
  // calling constructor for each index of encoder array
  //and initialize with the corresponding pins
  for (int i = 0; i < encoder_count; i++) {
    int MUX_A = encoderlist[i][0];
    int pin_A = encoderlist[i][1];
    int MUX_B = encoderlist[i][2];
    int pin_B = encoderlist[i][3];
    encoder_arr[i] = RotaryEncoder(MUX_A, MUX_A, pin_A, pin_B, RotaryEncoder::LatchMode::FOUR0);
  }
  Serial.begin(250000);
  Serial.println("Ready!");
  memset(io_time, millis(), sizeof(io_time));
  memset(io_states, 0, sizeof(io_states));
  initiateStates();
}


//******************************************************************************
//*********************************MAIN LOOP************************************
//******************************************************************************

void loop() {
  readButtonSwitches();
  readEncoders();
}




//******************************************************************************
//*********************************FUNCTIONS************************************
//******************************************************************************

void initiateStates() {
  for (int i = 0; i < mux_count; i ++) {
    for (int j = 0; j < 16; j ++) {
      io_states[ i ][ j ] = readMux(i, j);
    }
  }
}

int readButtonSwitches() {
  for (int i = 38; i < 38 + mux_count; i ++) {
    //Loop trough all MUX
    for (int j = 0; j < 16; j ++) {
      //Loop trough all Channels j of MUX i
      if (channel_is_stable(i - 38, j)) {
        switch (io_layout[ i - 38 ][ j ]) {
          case 'B':
            button_function(i, j);
            break;
          case 'S':
            switch_function(i, j);
            break;
          case 'R':
            relais_function(i, j);
            break;
        }//Switch
      }//Loop
    }//Loop
  }//for
}

int readMux(int mux, int channel) {
  int controlPin[] = {s0, s1, s2, s3};
  int muxChannel[16][4] = {
    {0, 0, 0, 0}, //channel 0
    {1, 0, 0, 0}, //channel 1
    {0, 1, 0, 0}, //channel 2
    {1, 1, 0, 0}, //channel 3
    {0, 0, 1, 0}, //channel 4
    {1, 0, 1, 0}, //channel 5
    {0, 1, 1, 0}, //channel 6
    {1, 1, 1, 0}, //channel 7
    {0, 0, 0, 1}, //channel 8
    {1, 0, 0, 1}, //channel 9
    {0, 1, 0, 1}, //channel 10
    {1, 1, 0, 1}, //channel 11
    {0, 0, 1, 1}, //channel 12
    {1, 0, 1, 1}, //channel 13
    {0, 1, 1, 1}, //channel 14
    {1, 1, 1, 1}  //channel 15
  };
  for (int i = 0; i < 4; i ++) {
    digitalWrite(controlPin[i], muxChannel[channel][i]);
  }
  //read the value at the SIG pin
  int val = digitalRead(mux);
  //return the inverse value
  val = 1 - val;
  return val;
}

bool channel_is_stable(int i, int j) {
  if (millis() - io_time[ i ][ j ] > debounceDelay) {
    return 1;
  } else {
    return 0;
  }
}

bool channel_is_old(int i, int j) {
  if (millis() - io_time[ i ][ j ] > repressDelay) {
    return 1;
  } else {
    return 0;
  }
}

// This function loops trough all encoders and gets the rotation data
void readEncoders() {
  for (int i = 0; i < encoder_count; i++) {
    readEncoder(i);
  }
}


void readEncoder(int i) {
  encoder_arr[i].tick();
  if (encoder_arr[i].isRotating()) { //Encoder is rotating
    String dir;
    String velocity;
    if ((int)encoder_arr[i].getDirection() == 1) {
      dir = "CW";
      //Serial.print("CW ");
    } else {
      dir = "CCW";
      //Serial.print("CCW ");
    }

    if (0 <= encoder_arr[i].getRPM() && encoder_arr[i].getRPM() < Speed_Threshhold) {
      velocity = "Slow";
    } else if (Speed_Threshhold <= encoder_arr[i].getRPM()) {
      velocity = "Fast";
    } else {
      velocity = "ERROR";
    }
    Serial.println("E." + String(i + 1) + "." + dir + "." + velocity);
  }
}//readEncoder


void button_function(int i, int j) {
  if (readMux(i, j) == 1 && channel_is_old(i - 38, j)) {
    io_time[ i - 38 ][ j ] = millis();
    io_states[ i - 38 ][ j ] = readMux(i, j);
    //Serial.println ("Button " + String(i) + "/" + String(j) + " pressed!");
    io_states[ i - 38 ][ j ] = 0;
    Serial.println("B." + String(i) + "." + String(j) + "." + "X");
  }
}

void switch_function(int i, int j) {
  if (readMux(i, j) != io_states[ i - 38 ][ j ] && channel_is_stable(i - 38, j)) {
    io_states[ i - 38 ][ j ] = readMux(i, j);
    io_time[ i - 38 ][ j ] = millis();
    if (readMux(i, j) == 1) {
      //Serial.println("Switch " + String(i) + "/" + String(j) + " flipped ON!");
      Serial.println("S." + String(i) + "." + String(j) + "." + "1");
    } else {
      Serial.println("S." + String(i) + "." + String(j) + "." + "0");
      //Serial.println("Switch " + String(i) + "/" + String(j) + " flipped OFF!");
    }
  }
}

void relais_function(int i, int j) {
  if (readMux(i, j) == 1 && channel_is_old(i - 38, j)) {
    io_time[ i - 38 ][ j ] = millis();
    io_states[ i - 38 ][ j ] = readMux(i, j);
    io_states[ i - 38 ][ j ] = 0;
    int rows =  sizeof relaislist / sizeof relaislist[0];
    for (int k = 0; k < rows; k ++) {
      if (relaislist[k][0] == i && relaislist[k][1] == j) {
        digitalWrite(relaislist[k][2], LOW); //turn Relais ON
        delay(50);
        digitalWrite(relaislist[k][2], HIGH); //turn Relais OFF
      }
    }
  }
}
