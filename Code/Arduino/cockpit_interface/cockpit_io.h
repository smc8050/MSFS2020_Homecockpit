#ifndef cockpit_io.h 
#define cockpit_io.h
char io_layout[14][16] = {
{'B','B','E','E','B','E','E','B','B','B','B','B','X','E','E','B'}, // MUX 38
{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 39
{'E','E','E','E','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 40
{'E','E','B','E','E','E','E','B','E','E','E','E','B','E','E','B'}, // MUX 41
{'B','B','E','E','B','E','E','B','B','B','B','B','B','E','E','B'}, // MUX 42
{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 43
{'E','E','E','E','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 44
{'B','B','S','S','X','X','S','S','S','S','S','S','S','S','S','S'}, // MUX 45
{'S','S','S','S','S','S','S','S','S','S','S','S','S','S','S','S'}, // MUX 46
{'S','S','S','S','S','S','S','S','S','S','S','S','S','S','S','S'}, // MUX 47
{'S','S','S','S','S','S','S','S','S','S','S','S','S','S','S','S'}, // MUX 48
{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 49
{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}, // MUX 50
{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}  // MUX 51
};
int encoderlist[ 17 ][ 4 ] = 
{
{38,2,38,3}, //Encoder 1
{38,5,38,6}, //Encoder 2
{38,13,38,14}, //Encoder 3
{40,0,40,1}, //Encoder 4
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
{44,0,44,1}, //Encoder 15
{44,2,44,3} //Encoder 16
};
int io_states[14][16];
int io_time[14][16];
int mux_count = 14;
#endif
