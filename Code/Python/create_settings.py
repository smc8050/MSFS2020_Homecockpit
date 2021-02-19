import pandas as pd
import json
import numpy as np

#path of the input CSV:
data_input_file = "Cockpit_config.CSV"
#column headers of the CSV:
csv_header = ["Arduino Pin","MUX channel","TYPE","Encoder Number","Sim Connect CMD"]

#following names should not be changed:
header_filename = "cockpit_io.h"
json_filename = "cockpit_config.json"



class csv_column:
  def __init__(self, csv_header):
    self.sig_pin = csv_header[0]
    self.mux_channel = csv_header[1]
    self.channel_type = csv_header[2]
    self.encoder_number = csv_header[3]
    self.sim_connect_cmd = csv_header[4]

csv_column = csv_column(csv_header)


#read csv
df = pd.read_csv(data_input_file, sep=';')

def create_header_file(df, header_file_name):
    ''' Creates header file

    This function creates the header file, which is used in the arduino

    :param df:pandas dataframe with loaded csv information
    :param header_file_name: filename of the header file
    '''

    header_file = open(f"{header_file_name}","w")
    head = f'#ifndef {header_file_name} \n#define {header_file_name}\n'
    header_file.write(head)

    write_io_layout_array(df, header_file)
    write_encoderlist_array(df, header_file)
    create_empty_arrays(df, header_file)

    header_file.write('#endif')
    header_file.close()



def create_config_json(df,json_filename):
    '''creates the cockpit_config.json

    The CSV file should be of following format:
    [Pin where the MUX SIG is connected on the Arduino];[MUX channel];[Encoder Number];[Sim Connect CMD]

    :param df: pandas dataframe with loaded csv information
    '''

    cockpit_config = {}

    #create button commands dictionary
    button_cmd = {}
    for index, row in df.iterrows():
        if row[csv_column.channel_type] == 'B':
            key = (str(row[csv_column.sig_pin]) + "_" + str(row[csv_column.mux_channel]))
            value = row[csv_column.encoder_number]
            button_cmd.update({key: value})
    cockpit_config["Button_commands"] = button_cmd

    # create switch commands dictionary
    switch_cmd = {}
    for index, row in df.iterrows():
        if row[csv_column.channel_type] == 'S':
            key = (str(row[csv_column.sig_pin]) + "_" + str(row[csv_column.mux_channel]))
            value = row[csv_column.encoder_number]
            switch_cmd.update({key: value})
    cockpit_config["Switch_commands"] = switch_cmd

    # create encoder commands dictionary
    encoder_cmd = {}
    for index, row in df.iterrows():
        if row[csv_column.channel_type] == 'EA' or row[csv_column.channel_type] == 'EB':
            key = (str(row[csv_column.encoder_number]))
            value = (str(row[csv_column.encoder_number]))
            if key not in encoder_cmd and not key == 'nan':
                encoder_cmd.update({key[:-2]: value})
    cockpit_config["Encoder_commands"] = encoder_cmd

    #save to JSON file
    out_file = open(json_filename, "w")
    json.dump(cockpit_config, out_file, indent=6)
    out_file.close()

def write_io_layout_array(df, header_file):
    ''' writes io_layout array to header file

    The io_layout array stores all the information of the attached hardware at a selected channel.
    columns -> multiplexer channels 0 to 15
    rows -> different multiplexers
    Possible values:
        S     -> Switch
        B     -> Button
        EA/EB -> Encoder pin A/B
        X     -> Not in use

    Example:
    What is connected on MUX 3, channel 5?
    -> io_layout[2=(3-1)][5]

    :param df: pandas dataframe with loaded csv information
    :param header_file: TextIOWrapper with open header file to write
    '''

    mux_pins = df[csv_column.sig_pin].unique()
    io_layout_arr = np.full((mux_pins.__len__(), 16), 'X')
    i = 0
    for mux_number in mux_pins:
        selected_mux = df.loc[df[csv_column.sig_pin] == mux_number]
        j = 0
        for index, row in selected_mux.iterrows():
            channel_type = str(row[csv_column.channel_type])
            io_layout_arr[i][j] = channel_type
            j += 1
        i += 1

    array_def = f"char io_layout[{mux_pins.__len__()}][16] = {{\n"
    header_file.write(array_def)
    i = 0
    for mux_number in mux_pins:
        j = 0
        header_file.write("{")
        for j in range(0,15,1):
            channel_type = io_layout_arr[i][j]
            header_file.write(f'\'{channel_type}\',')
            j += 1
        if i != mux_pins.__len__()-1: #if not last MUX, add new line to array
            channel_type = io_layout_arr[i][j]
            header_file.write(f'\'{channel_type}\'}}, // MUX {mux_number}\n')
        else: #if last MUX, add line and close array definition
            channel_type = io_layout_arr[i][j]
            header_file.write(f'\'{channel_type}\'}}  // MUX {mux_number}\n')
            header_file.write('};\n')
        i += 1

def write_encoderlist_array(df, header_file):
    ''' writes the encoderlist array to the header file

    This function creates an array where each row contains following data:
    {[MUX_A],[Channel_A],[MUX_A],[Channel_A]}

    :param df: pandas dataframe with loaded csv information
    :param header_file: TextIOWrapper with open header file to write

    '''
    encodercount = df[csv_column.encoder_number].unique().__len__()
    header_file.write(f"int encoderlist[ {encodercount} ][ 4 ] = \n{{\n")
    for i in range(1,encodercount,1):
        selected_encoder = df.loc[df[csv_column.encoder_number] == i]
        encoderA = selected_encoder.loc[df[csv_column.channel_type] == 'EA'][csv_column.mux_channel].values[0]
        encoderB = selected_encoder.loc[df[csv_column.channel_type] == 'EB'][csv_column.mux_channel].values[0]
        muxA = selected_encoder.loc[df[csv_column.channel_type] == 'EA'][csv_column.sig_pin].values[0]
        muxB = selected_encoder.loc[df[csv_column.channel_type] == 'EB'][csv_column.sig_pin].values[0]
        if i != encodercount-1: #if not last encoder, add new line to array
            header_file.write(f'{{{muxA},{encoderA},{muxB},{encoderB}}}, //Encoder {i}\n')
        else: #if last encoder, add line and close array definition
            header_file.write(f'{{{muxA},{encoderA},{muxB},{encoderB}}} //Encoder {i}\n')
            header_file.write('};\n')


def create_instrument_json(df):
    #TODO
    print("creating_instrument")

def create_empty_arrays(df, header_file):
    print("creating_instrument")
    mux_count = df[csv_column.sig_pin].unique().__len__()
    header_file.write(f"int io_states[{mux_count}][16];\n")
    header_file.write(f"int io_time[{mux_count}][16];\n")
    header_file.write(f"int mux_count = {mux_count};\n")


if __name__ == '__main__':
    create_config_json(df, json_filename)  # create json
    create_header_file(df, header_filename) # create header
