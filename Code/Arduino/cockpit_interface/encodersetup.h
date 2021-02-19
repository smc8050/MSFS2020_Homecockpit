#ifndef encodersetup
#define encodersetup
 // this 2D array stores information about the respective pins of the multiplexed encoders
 // with the following format:
 //{[MUX Signal of Encoderpin A],[MUX Channel of Encoderpin A],
 // [MUX Signal of Encoderpin B],[MUX Channel of Encoderpin A]}
 // for every encoder one row
int encoderlist[ 22 ][ 4 ] = 
{
{38,2,38,3},
{38,5,38,6},
{38,14,38,13},
{41,15,40,0},
{40,2,40,3},
{41,0,41,1},
{41,3,41,4},
{41,5,41,6},
{41,8,41,9},
{41,10,41,11},
{41,13,41,14},
{42,2,42,3},
{42,5,42,6},
{42,14,42,13},
{45,15,44,0},
{44,2,44,3},
{45,0,45,1},
{45,3,45,4},
{45,5,45,6},
{45,8,45,9},
{45,10,45,11},
{45,13,45,14}
};
#endif
