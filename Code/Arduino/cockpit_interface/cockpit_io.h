 // these 2D array store information about the respective pins where: 2DArray[MUX_Pin][MUX_Channel]
 // io_layout: defines which pins on the MUX are Buttons (B), switches (S), or encoders (E)
 // io_states: used to store last state of the pin
 // io_time: used to store last timestamp of change of the pin to debounce an input
#ifndef cockpit_io
#define cockpit_io
char io_layout[ 14 ][ 16 ] = {{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'},{'B','B','B','B','B','B','B','B','B','B','B','B','B','B','B','B'}};
int io_states[ 14 ][ 16 ];
int io_time[ 14 ][ 16 ];
int mux_count = 14;
#endif
