import json
import time
import warnings
import serial
import serial.tools.list_ports
from SimConnect import *
from Instrument_popout_utils import *


def getArduinoPort():
    '''Gets Arduino Port number

    This function loops trough all ports and check if the names contain 'Arduino' and selects the first Port if multiple
    arduinos are connected.

    :return: ser.port
    :type: String
    '''
    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'Arduino' in p.description  # may need tweaking to match new arduinos
    ]
    if not arduino_ports:
        raise IOError("No Arduino found")
    if len(arduino_ports) > 1:
        warnings.warn('Multiple Arduinos found - using the first')
    ser = serial.Serial(arduino_ports[0])
    return ser.port


def ConnectArduinoSerial(gui, baudrate):
    '''Connect to Arduino

    This functions opens a serial connection to the Arduino via USB with the specified baudrate.
    After the connection attempt the GUI will be updated accordingly.

    :param gui: the Gui Object window
    :type gui: PyQt window object
    :param baudrate: The baudrate with which the connection will be opened
    :type baudrate: Int
    :return: Nothing
    '''
    try:
        if gui.arduino == None:
            gui.arduino = serial.Serial(getArduinoPort(), baudrate, timeout=.1)
            print("Connected to Arduino")
        else:
            if not gui.arduino.is_open:
                gui.arduino.open()
        gui.arduino_state.setText("Connected!")
        gui.arduino_state.setStyleSheet('color: green')

    except:
        print('Could not connect to arduino!')
        gui.arduino_state.setText("Error")
        gui.arduino_state.setStyleSheet('color: red')


def StartSimConnect(gui):
    '''Create SimConnect link

    This Function opens the connection to the FLight Simulator via the SimConnect Interface.
    The connection will be saved in the GUI Window object in the object AircraftEvents.

    :param gui: the Gui Object window
    :type gui: PyQt window object
    :return: Nothing
    '''
    Debug = False
    if not Debug:
        try:
            global SimConnect
            global AircraftEvents
            global AircraftRequests
            SimConnect = SimConnect()
            gui.AircraftEvents = AircraftEvents(SimConnect)
            gui.AircraftRequests = AircraftRequests(SimConnect, _time=0)
            print("Connected to Microsoft Flight Simulator 2020!")
            gui.MSFS_State.setText("Connected!")
            gui.MSFS_State.setStyleSheet('color: green')
        except:
            print("No connection to Microsoft Flight Simulator 2020!")
            gui.MSFS_State.setText("Error")
            gui.MSFS_State.setStyleSheet('color: red')


def get_config(config_file):
    """ Reads Config file

    This functions reads the config file and returns the information
    :param config_file: name of the config file as string
    :return: object with config information
    """
    with open(config_file, 'r') as myfile:
        data = myfile.read()
    return json.loads(data)


# reads JSON and extracts the command connected with pin "channel" on Multiplexer pin "mux"
# executes the read command in MSFS2020 with the function execudeCMD
def sendSwitchCommand(mux, channel, state, gui, AircraftEvents):
    ''' Send Switch Command to Flight Simulator

    This Function receives the Information submitted from the Arduino, reads the command associated to this information
    from the JSON file and sends this command tho the executeCMD function, which executes the command
    in the Flight Simulator. Depending on the Command the CMD variable gets modified if the command is a Switch which
    can have two states On (1) or Off (2), ON/OFF will be appended the the command.

    :param mux: MUX Number (38-48)
    :param channel: Channel Number (0-15)
    :param state: State of the command received (1, 0, X)
    :param gui: The PyQt Window object is needed to be updated
    :param AircraftEvents: SimConnect Object which will execute the Command
    :return: Nothing
    '''

    config = get_config('cockpit_config.json')
    cmd = str(config["SwitchCMD"][mux + "_" + channel])
    if cmd[-1] == '_':
        if state == '1':
            cmd = cmd + 'ON'
        else:
            cmd = cmd + 'OFF'
    executeCMD(cmd, gui, AircraftEvents)


def sendButtonCommand(mux, channel, gui, AircraftEvents):
    ''' Send Button Command to Flight Simulator

    This Function receives the Information submitted from the Arduino, reads the command associated to this information
    from the JSON file and sends this command tho the executeCMD function, which executes the command
    in the Flight Simulator.

    :param mux: MUX Number (38-48)
    :param channel: Channel Number (0-15)
    :param gui: The PyQt Window object is needed to be updated
    :param AircraftEvents: SimConnect Object which will execute the Command
    :return: Nothing
    '''
    config = get_config('cockpit_config.json')
    executeCMD(str(config["ButtonCMD"][mux + "_" + channel]), gui, AircraftEvents)


def readJSON(file, chapter, value):
    ''' Reas a JSON file

    This function reads the command saved in the JSON dictionary file and returns it

    :param file: Location of the JSON File
    :param chapter: JSON Chapter
    :param value: Value which will be searched for in the JSON dictionary
    :return: Looked up value
    '''
    config = get_config('cockpit_config.json')
    return config[chapter][value]


def update_gui_cmd_status(gui, text, color, cmd):
    """ Updates Gui

    This function updates the gui after a command is sent
    :param gui: window object
    :param text: string which will be displayed (Error/Received)
    :param color: color of the text
    :param cmd: command string
    :return: none
    """
    gui.last_cmd_status.setText(text)
    gui.last_cmd_status.adjustSize()
    gui.last_cmd_status.setStyleSheet(f'color: {color}')
    gui.last_cmd_sent.setText(cmd)


def executeCMD(cmd, gui, AircraftEvents):
    ''' Executes the submitted command

    Executes the received command in MSFS 2020 via SimConnect Interface, and updates the GUI accordingly

    :param cmd: simconnect command as string
    :param gui:
    :param AircraftEvents:
    :return:
    '''
    try:
        # Trigger a simple event
        # event_to_trigger = gui.AircraftEvents.find(CMD) #OLD
        # event_to_trigger() #OLD
        cmd_bytes = cmd.encode('utf-8')
        send_event = Event(cmd_bytes, SimConnect)
        send_event()
        print("CMD SENT: " + cmd)
        update_gui_cmd_status(gui, "Received", "green", cmd)
    except:
        print("Error, " + cmd + " not accepted by SimConnect")
        update_gui_cmd_status(gui, "ERROR", "red", cmd)



class parseserial():
    ''' Parsing the Serial data

        Reads the incoming serial strings and splits it into array
        String Pattern: [Type].[Mux number].[Channel number].[State]
        [Type] => S(Switch), B(Button), A/B(Encoder)
        [Mux number] => Integer from 38 upwards
        [Channel number] => Integer from 0 to 15
        [State] => X if no state, 1/0 (ON/Off) if Switch

    '''

    def __init__(self, serialString):
        if serialString != "Ready!":
            # serialString = serialString[:-1]  # removes last char, so the string has now the format 38.1
            splittedString = serialString.split('.')
            self.type = splittedString[0]
            self.mux = splittedString[1]
            self.channel = splittedString[2]
            self.state = splittedString[3]
            self.fullstring = serialString
        else:
            self.type = 0
            self.mux = 0
            self.channel = 0
            self.state = 0
            self.fullstring = 0


def readSerialArduino(gui, arduino, AircraftEvents):
    while gui.runThread:
        try:
            data = arduino.readline()[:-2]  # the last bit gets rid of the new-line chars
            if data:
                try:
                    receivedString = parseserial(data.decode('utf-8'))
                    if receivedString.fullstring == "B.43.3.X": #This is a special button used to pop out the windows in the flight simulator
                        print("Setup Instrument displays")
                        setup_instrument_diplays(gui)
                        update_gui_cmd_status(gui, "Received", "green", "Setup instrument displays")
                    elif receivedString.type == "B":  # call Push button routine
                        print(receivedString.fullstring)
                        sendButtonCommand(receivedString.mux, receivedString.channel, gui, AircraftEvents)
                    elif receivedString.type == "S":  # call Switch routine
                        print(receivedString.fullstring)
                        sendSwitchCommand(receivedString.mux, receivedString.channel, receivedString.state, gui)
                    elif receivedString.type == "A" or receivedString.type == "B":
                        # TODO: call Encoder routine
                        # encoder(receivedString.mux, receivedString.channel, receivedString.type)
                        # print("Encoder: " + receivedString.mux + "_" + receivedString.channel +"-"+ receivedString.type )
                        print(receivedString.fullstring)
                    else:
                        print("Connection to Arduino established!")
                except:
                    print("An exception occurred")
        except:
            print("No Connection to arduino, try to reconnect...")
            if arduino != None:
                arduino.close()
            ConnectArduinoSerial(gui, 250000)
            time.sleep(2)


