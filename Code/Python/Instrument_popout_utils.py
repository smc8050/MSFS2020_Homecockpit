import json
import os
import time

import pydirectinput

import win32api, win32con
from pywinauto import Desktop, Application



def popoutwindows(coordinates):
    ''' Popout Instrument Displays

    This Function pops out  the instruments display trough emulating pressing ALT and click on the display (Coordinates)
    :return:
    '''

    # TODO: implement loop trough list and popup multiple windows (give coordinates in 2D Array?)

    # time.sleep(5) #for debugging
    pydirectinput.keyDown("alt")  # Holds down the alt key
    leftClick(coordinates.PFD_x, coordinates.PFD_y)  # Popout PFD
    time.sleep(0.05)
    leftClick(coordinates.MFD_x, coordinates.MFD_y)  # Popout MFD
    pydirectinput.keyUp("alt")  # releases the alt key
    time.sleep(0.05)
    leftClick(coordinates.Expand_x,
              coordinates.Expand_y)  # Split popout into different windows (press magnifying glass in MSFS)


def leftClick(x_pos, y_pos):
    ''' Sends Left click

    This Function sends a Left click on the specified coordinates

    :param x_pos: X Coordinate of click
    :param y_pos: Y Coordinate of click
    :return:
    '''
    win32api.SetCursorPos((x_pos, y_pos))
    time.sleep(.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    print('Left Click at: ' + str(x_pos) + "/" + str(y_pos))


def getpid(process_name):
    ''' Gets the PID from process

    :param process_name: Processs name of which the PID should be returned
    :return: PID
    '''
    list = [item.split()[1] for item in os.popen('tasklist').read().splitlines()[4:] if process_name in item.split()]
    return int(list[0])


def move_popoutwindows():
    '''
    This function moves the windows of the PFD and MFD G1000 to the specified cooredinates
    TODO: read coordinates from file
    :return:
    '''

    FlightSim_PID = getpid("FlightSimulator.exe")  # gets PID
    window_list = Desktop(backend="win32").windows(process=FlightSim_PID)  # List of all windows?

    j = 0  # counter for list
    PopupWindow_Number = []  # Create empty List -> will be filled with window number of MFD and PFD
    for i in window_list:
        name = i._element_info.name
        classname = i.friendlyclassname
        j = j + 1
        if name == '' and classname == 'AceApp':
            PopupWindow_Number.append(j - 1)  # save popup windowsnumber in List
    try:
        Desktop(backend="win32").windows(process=FlightSim_PID)[PopupWindow_Number[0]].move_window(x=2700, y=2200,
                                                                                                   width=1000,
                                                                                                   height=800,
                                                                                                   repaint=True)
        print("moved MFD window")
        Desktop(backend="win32").windows(process=FlightSim_PID)[PopupWindow_Number[1]].move_window(x=0, y=2200,
                                                                                                   width=1000,
                                                                                                   height=800,
                                                                                                   repaint=True)
        print("moved PFD window")

    except:
        print("no Popup Windows Found")

    Application().connect(process=FlightSim_PID).top_window().set_focus()  # Set Focus to FS Main Window


class instrument_coordinates():
    '''
    This class reads the "click" coordinades depending on the currently selected airplane
    '''

    def __init__(self, gui, file):
        with open(file, 'r') as myfile:
            data = myfile.read()
        obj = json.loads(data)

        aircraft_model = self.getAircraftModel(gui)

        self.PFD_x = int(obj[aircraft_model]["PFD_x"])
        self.PFD_y = int(obj[aircraft_model]["PFD_y"])
        self.MFD_x = int(obj[aircraft_model]["MFD_x"])
        self.MFD_y = int(obj[aircraft_model]["MFD_y"])
        self.Expand_x = int(obj[aircraft_model]["Expand_x"])
        self.Expand_y = int(obj[aircraft_model]["Expand_y"])

    def getAircraftModel(self, gui):
        '''
        This Function returns the current User-Aircraft model in the game

        :param gui: PyQt Window object
        :return: Aircraftmodel as string
        '''
        model = gui.AircraftRequests.get("ATC_MODEL")
        model_shorted = str(model)[21:(len(str(model)) - 8)]
        print("Model is: " + model_shorted)
        return model_shorted


def setup_instrument_diplays(gui):
    """
    When this function is called the windows are poped our in the Flight Sim with 3 Steps:
    1: get coordinates of where to click on the monitor
    2: Emulating a user interaction with the mouse to click on the displays tho pop them out to new windows
    3: Moving and resizing the popped out windows TODO: reading coordinates from the file, now they are hardcoded
    :param gui:
    :return:
    """
    coordinates = instrument_coordinates(gui, "instrument_displays.json")
    popoutwindows(coordinates)
    move_popoutwindows()
