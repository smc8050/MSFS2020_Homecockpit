// -----
// MultiplexedRotaryEncoder.h - Library for using rotary encoders.
// This class is implemented for use with the Arduino environment.
//
// Copyright (c) by Matthias Hertel, http://www.mathertel.de
//
// This work is licensed under a BSD 3-Clause style license,
// https://www.mathertel.de/License.aspx.
//
// More information on: http://www.mathertel.de/Arduino
// -----
// 18.01.2014 created by Matthias Hertel
// 16.06.2019 pin initialization using INPUT_PULLUP
// 10.11.2020 Added the ability to obtain the encoder RPM
// 29.01.2021 Options for using rotary encoders with 2 state changes per latch.
// 20.02.2021 Modified by Steivan Claglüna for Multiplexing Encoders (renamed from RotaryEncoder to MultiplexedRotaryEncoder)
// -----

#ifndef MultiplexedRotaryEncoder_h
#define MultiplexedRotaryEncoder_h

#include "Arduino.h"

class RotaryEncoder
{
public:
  enum class Direction {
    NOROTATION = 0,
    CLOCKWISE = 1,
    COUNTERCLOCKWISE = -1
  };
  
	//Mux control pins
	int s0 = 22;
	int s1 = 23;
	int s2 = 24;
	int s3 = 25;
	
	//Encoder pins A and B
	int _MUX_A;
	int _MUX_B;
	int _channel_A;
	int _channel_B;

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
	  //Serial.print("Value: "); Serial.println(val);
	  return val;
	}


  enum class LatchMode {
    FOUR3 = 1, // 4 steps, Latch at position 3 only (compatible to older versions)
    FOUR0 = 2, // 4 steps, Latch at position 0 (reverse wirings)
    TWO03 = 3  // 2 steps, Latch at position 0 and 3 
  };

  // ----- Constructor -----
  RotaryEncoder(int _MUX_A, int _MUX_B, int _channel_A, int _channel_B, LatchMode mode);

  // retrieve the current position
  long getPosition();

  // simple retrieve of the direction the knob was rotated at. 0 = No rotation, 1 = Clockwise, -1 = Counter Clockwise
  Direction getDirection();

  // adjust the current position
  void setPosition(long newPosition);

  // call this function every some milliseconds or by using an interrupt for handling state changes of the rotary encoder.
  void tick();
  
  //check if the encoder is rotating
  bool isRotating();

  // Returns the time in milliseconds between the current observed
  unsigned long getMillisBetweenRotations() const;

  // Returns the RPM
  unsigned long getRPM();
  


private:
  
  LatchMode _mode; // Latch mode from initialization

  volatile int8_t _oldState;
  
  volatile long _position;        // Internal position (4 times _positionExt)
  volatile long _positionExt;     // External position
  volatile long _positionExtPrev; // External position (used only for direction checking)

  unsigned long _positionExtTime;     // The time the last position change was detected.
  unsigned long _positionExtTimePrev; // The time the previous position change was detected.
};

#endif

// End