#include "encodersetup.h"
#include "cockpit_io.h"
#include "Rotary.h"
//Mux control pins
int s0 = 22;
int s1 = 23;
int s2 = 24;
int s3 = 25;

// Variables will change:
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

void setup() {
  pinMode(s0, OUTPUT); 
  pinMode(s1, OUTPUT); 
  pinMode(s2, OUTPUT); 
  pinMode(s3, OUTPUT); 

  digitalWrite(s0, LOW);
  digitalWrite(s1, LOW);
  digitalWrite(s2, LOW);
  digitalWrite(s3, LOW);
  
  pinMode(38, INPUT_PULLUP);
  pinMode(39, INPUT_PULLUP);
  pinMode(40, INPUT_PULLUP);
  pinMode(41, INPUT_PULLUP);
  pinMode(42, INPUT_PULLUP);
  pinMode(43, INPUT_PULLUP);
  pinMode(44, INPUT_PULLUP);
  pinMode(45, INPUT_PULLUP);
  pinMode(46, INPUT_PULLUP);
  pinMode(47, INPUT_PULLUP);
  pinMode(48, INPUT_PULLUP);
  pinMode(49, INPUT_PULLUP);
  pinMode(50, INPUT_PULLUP);
  pinMode(51, INPUT_PULLUP);
  pinMode(52, INPUT_PULLUP);
  
  Serial.begin(250000);
  Serial.println("Ready!");
  memset(io_time,millis(),sizeof(io_time));
  memset(io_states,0,sizeof(io_states));
  initiateEncoders();
  initiateStates();
}

void loop() {
  for(int i = 38; i < 38 + mux_count; i ++){
    for(int j = 0; j < 16; j ++){
      if (channel_is_stable(i-38,j)){
        switch (io_layout[ i-38 ][ j ]) {
          case 'B':
            button_function(i,j);
            break;
          case 'S':
            switch_function(i,j);
            break;
          case 'E':
            // Call Encoder function
            //Serial.println("Encoder");
            break;
          default:
            // statements
            break;
        }
      }
    }
  }
}



// All function below:

//This function reads all state of the pins of all encoder and stores it in the encodercube
void initiateEncoders(){
  int encodercount = sizeof (encodercube) / sizeof (encodercube[0]);
  for(int i = 0; i < encodercount; i ++){
    //read Pin A
    int initialState_A = readMux(encodercube[ i ][ 1 ][ 0 ], encodercube[ i ][ 1 ][ 1 ]);
    //store current state of pin A
    encodercube[ i ][ 0 ][ 0 ] = initialState_A;
    
    //read Pin B
    int initialState_B = readMux(encodercube[ i ][ 2 ][ 0 ], encodercube[ i ][ 2 ][ 1 ]);
    //store current state of pin B
    encodercube[ i ][ 0 ][ 1 ] = initialState_B;
  }
}


void initiateStates(){
  for(int i = 0; i < mux_count; i ++){
    for(int j = 0; j < 16; j ++){
      io_states[ i ][ j ] = readMux(i,j);
    }
  }
}


int readMux(int mux, int channel){
  int controlPin[] = {s0, s1, s2, s3};
  int muxChannel[16][4]={
   {0,0,0,0}, //channel 0
   {1,0,0,0}, //channel 1
   {0,1,0,0}, //channel 2
   {1,1,0,0}, //channel 3
   {0,0,1,0}, //channel 4
   {1,0,1,0}, //channel 5
   {0,1,1,0}, //channel 6
   {1,1,1,0}, //channel 7
   {0,0,0,1}, //channel 8
   {1,0,0,1}, //channel 9
   {0,1,0,1}, //channel 10
   {1,1,0,1}, //channel 11
   {0,0,1,1}, //channel 12
   {1,0,1,1}, //channel 13
   {0,1,1,1}, //channel 14
   {1,1,1,1}  //channel 15
 };

  for(int i = 0; i < 4; i ++){
    digitalWrite(controlPin[i], muxChannel[channel][i]);
  }
  //read the value at the SIG pin
  int val = digitalRead(mux);
  //return the inverse value
  val = 1 - val;
  return val;
}


void ReadEncoders(){
  int encodercount = sizeof (encodercube) / sizeof (encodercube[0]);
  for(int i = 0; i < encodercount; i ++){
    int lastState_A = encodercube[ i ][ 0 ][ 0 ];
    int lastState_B = encodercube[ i ][ 0 ][ 1 ];
    int currentState_A = readMux(encodercube[ i ][ 1 ][ 0 ], encodercube[ i ][ 1 ][ 1 ]);
    int currentState_B = readMux(encodercube[ i ][ 2 ][ 0 ], encodercube[ i ][ 2 ][ 1 ]);
    //Compare current state of A to the last state stored in the encoder cube
    if (lastState_A != currentState_A) { // if they are not equal it means the encoder has moved
      if (currentState_A != currentState_B) {
        //Clockwise rotation
        Serial.println("CW");
      } else {
        //Counterclockwise rotation
        Serial.println("CCW");
      }
    }
  }
}

bool channel_is_stable(int i,int j){
if (millis()-io_time[ i ][ j ]>debounceDelay) {
    return 1;
  } else {
    return 0;
  }
}

bool channel_is_old(int i,int j){
if (millis()-io_time[ i ][ j ]>repressDelay) {
    return 1;
  } else {
    return 0;
  }
}


void button_function(int i,int j){
  if (readMux(i,j) == 1 && channel_is_old(i-38,j)){
  io_time[ i-38 ][ j ] = millis();
  io_states[ i-38 ][ j ] = readMux(i,j);
  //Serial.println ("Button " + String(i) + "/" + String(j) + " pressed!");
  io_states[ i-38 ][ j ] = 0;
  Serial.println("B."+String(i)+"."+String(j)+"."+"X");
  }
}

void switch_function(int i,int j){
  if (readMux(i,j) != io_states[ i-38 ][ j ] && channel_is_stable(i-38,j)){
  io_states[ i-38 ][ j ] = readMux(i,j);
  io_time[ i-38 ][ j ] = millis();
  if (readMux(i,j)==1){
    //Serial.println("Switch " + String(i) + "/" + String(j) + " flipped ON!");
    Serial.println("S."+String(i)+"."+String(j)+"."+"1");
  } else {
    Serial.println("S."+String(i)+"."+String(j)+"."+"0");
    //Serial.println("Switch " + String(i) + "/" + String(j) + " flipped OFF!");
  }
  }
}
