#ifndef cockpit_io.h 
#define cockpit_io.h
char io_layout[9][16] = {
{'B','B','E','B','E','E','E','B','B','B','B','B','X','E','E','B'}, // MUX 38
{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 39
{'E','B','E','E','R','R','R','R','B','B','B','B','B','B','B','B'}, // MUX 40
{'E','E','B','E','E','E','E','B','E','E','E','E','B','E','E','E'}, // MUX 41
{'B','B','E','E','B','E','E','B','B','B','B','B','B','E','E','B'}, // MUX 42
{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 43
{'E','E','E','E','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 44
{'B','B','S','S','S','X','S','S','S','S','B','B','B','B','B','B'}, // MUX 45
{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}  // MUX 46
};
int encoderlist[ 16 ][ 4 ] = 
{
{38,2,38,4}, //Encoder 1
{38,5,38,6}, //Encoder 2
{38,13,38,14}, //Encoder 3
{40,0,41,15}, //Encoder 4
{40,2,40,3}, //Encoder 5
{41,0,41,1}, //Encoder 6
{41,3,41,4}, //Encoder 7
{41,5,41,6}, //Encoder 8
{41,8,41,9}, //Encoder 9
{41,10,41,11}, //Encoder 10
{41,13,41,14}, //Encoder 11
{42,2,42,3}, //Encoder 12
{42,5,42,6}, //Encoder 13
{42,13,42,14}, //Encoder 14
{44,0,44,1} //Encoder 15
};
int relaislist[ 4 ][ 3 ] = 
{
{40,4,50}, //Relais 0
{40,5,51}, //Relais 1
{40,6,52}, //Relais 2
{40,7,53} //Relais 3
};
int io_states[9][16];
int io_time[9][16];
int mux_count = 9;
#endif
