import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from simconnect_utils import *

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    finished = pyqtSignal()
    error_exit = pyqtSignal()


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        self.fn(*self.args)
        arg = self.queue.get()
        self.fun(arg)
        self.queue.task_done()
        self.signals.finished.emit()  # Done


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()

        self.threadpool = QThreadPool()  # Initialize threadpool

        # load stylesheet for GUI
        stylesheet_file = "simconnect_helper.stylesheet"
        with open(stylesheet_file, "r") as fh:
            self.setStyleSheet(fh.read())

    # this function starts the thread (thus the GUI stays responsive)
    def readSerialThread(self):
        """
        Starts a thread which constantly reads the serial output from the Arduino
        :rtype: object
        """
        self.worker = Worker(readSerialArduino, self, self.arduino, self.AircraftEvents)
        # worker.signals.finished.connect(self.ArduinoConnected) #fuctions which would be executed if thread is
        # finished (which will never happen here) Execute worker load thread
        print("Thread started...")
        self.threadpool.start(self.worker)

    def Connect(self):
        """
        Connects to the Arduino via Serial connection and to the Flight simulator via the SimConnect interface
        Starts a thread which constantly listens to the Serial connection
        :rtype: none
        """
        ConnectArduinoSerial(self, 250000)
        StartSimConnect(self)
        self.readSerialThread()

    def Reconnect(self):
        """
        Under Cunstruction
        In future: close all connections and stop the thread and then restart everything
        """
        print("Reconnecting...")
        # stop serial connection
        try:
            self.arduino.close()
        except:
            print("No Arduino Connected")
        self.AircraftEvents = None
        self.AircraftRequests = None
        self.Connect()

    def resetCMD(self):
        """
        Resets the value of the "last_cmd_sent" text on the GUI
        """
        self.last_cmd_sent.setText("-")
        self.last_cmd_status.setText("-")
        self.last_cmd_status.setStyleSheet('color: black')

    def sendCMD(self, CMD):
        """
        Helper function to send a command string to the flight simulator

        :param CMD: This command will be executed in MSFS
        :type CMD: str
        """
        executeCMD(CMD, self, self.AircraftEvents)

    # this function quits the programm
    def quit_programm(self):
        """
        Set the runThread flag to False will terminate the readSerial Thread. After that the programm will be closed
        """
        print("Prgram will be closed")
        self.runThread = False
        self.close
        sys.exit(0)

    def initUI(self):
        """
        this function initializes the GUI
        """

        # define Variables which are used from the GUI
        self.arduino = None
        self.AircraftEvents = None
        self.AircraftRequests = None
        self.runThread = True

        # set Gui icon folder
        self.gui_icon_folder = "gui_icons/"

        # GUI main dimensions and title
        self.setGeometry(3000, 200, 430, 470)
        self.setWindowTitle("Sim Connect Helper")

        # ConnectButton -> in Construction
        self.connect_btn = QtWidgets.QPushButton(self)
        self.connect_btn.setText("Reconnect")
        self.connect_btn.move(40, 80)
        self.connect_btn.resize(350, 50)
        # self.connect_btn.clicked.connect(self.readSerialThread)
        # self.connect_btn.clicked.connect(self.Reconnect())
        self.connect_btn.setIcon(QtGui.QIcon("./" + self.gui_icon_folder + "document-save-2.png"))
        self.connect_btn.setIconSize(QtCore.QSize(30, 30))
        self.connect_btn.setEnabled(False)  # Cannot be used until reconnect function is implemented

        # Connection Status Label
        self.connection_label = QtWidgets.QLabel(self)
        self.connection_label.setText("Connection Status:")
        self.connection_label.move(50, 140)
        self.connection_label.adjustSize()
        self.connection_label.setWordWrap(True)

        # Arduino State
        self.arduino_label = QtWidgets.QLabel(self)
        self.arduino_label.setText("Arduino:")
        self.arduino_label.move(50, 165)
        self.arduino_label.adjustSize()

        self.arduino_state = QtWidgets.QLabel(self)
        self.arduino_state.setText("-")
        self.arduino_state.move(140, 165)
        self.arduino_state.resize(150, 20)
        self.arduino_state.setStyleSheet('color: black')

        # MSFS State
        self.MSFS_label = QtWidgets.QLabel(self)
        self.MSFS_label.setText("Flight Sim:")
        self.MSFS_label.move(50, 190)
        self.MSFS_label.adjustSize()

        self.MSFS_State = QtWidgets.QLabel(self)
        self.MSFS_State.setText("-")
        self.MSFS_State.move(140, 190)
        self.MSFS_State.resize(150, 20)
        self.MSFS_State.setStyleSheet('color: black')

        # Manual Command label
        self.connection_label = QtWidgets.QLabel(self)
        self.connection_label.setText("Manual Command:")
        self.connection_label.move(50, 225)
        self.connection_label.adjustSize()
        self.connection_label.setWordWrap(True)

        # Manual Command textbox
        self.manual_cmd_textbox = QLineEdit(self)
        self.manual_cmd_textbox.move(50, 250)
        self.manual_cmd_textbox.resize(250, 25)
        self.manual_cmd_textbox.setPlaceholderText("Type Manual command")

        # Manual Command Button
        self.send_manual_btn = QtWidgets.QPushButton(self)
        self.send_manual_btn.setText("Send")
        self.send_manual_btn.move(320, 248)
        self.send_manual_btn.resize(70, 30)
        self.send_manual_btn.clicked.connect(lambda: self.sendCMD(self.manual_cmd_textbox.text()))
        self.send_manual_btn.setIconSize(QtCore.QSize(30, 30))

        # Last Command label
        self.last_cmd = QtWidgets.QLabel(self)
        self.last_cmd.setText("Last sent command:")
        self.last_cmd.move(50, 290)
        self.last_cmd.adjustSize()
        self.last_cmd.setWordWrap(True)

        # Last Command status
        self.last_cmd_status = QtWidgets.QLabel(self)
        self.last_cmd_status.setText("-")
        self.last_cmd_status.move(200, 290)
        self.last_cmd_status.adjustSize()
        self.last_cmd_status.setWordWrap(True)
        self.last_cmd_status.setStyleSheet('color: black')

        # Last Command sent
        self.last_cmd_sent = QtWidgets.QLabel(self)
        self.last_cmd_sent.setText("-")
        self.last_cmd_sent.move(50, 315)
        self.last_cmd_sent.resize(250, 25)
        self.last_cmd_sent.setWordWrap(True)

        # Manual Command Button
        self.reset_btn = QtWidgets.QPushButton(self)
        self.reset_btn.setText("Reset")
        self.reset_btn.move(320, 315)
        self.reset_btn.resize(70, 30)
        self.reset_btn.clicked.connect(self.resetCMD)
        self.reset_btn.setIconSize(QtCore.QSize(30, 30))

        # Quit Button
        self.quit_btn = QtWidgets.QPushButton(self)
        self.quit_btn.setText("Quit")
        self.quit_btn.move(40, 390)
        self.quit_btn.resize(350, 50)
        self.quit_btn.clicked.connect(self.quit_programm)
        self.quit_btn.setIcon(QtGui.QIcon("./" + self.gui_icon_folder + "application-exit-2.png"))
        self.quit_btn.setIconSize(QtCore.QSize(30, 30))

        # Version Label
        self.version_label = QtWidgets.QLabel(self)
        self.version_label.setText("V0.1")
        self.version_label.move(0, 445)
        self.version_label.resize(430, 20)
        self.version_label.setAlignment(Qt.AlignCenter)


def window():
    """
    this function opens the GUI window
    """

    app = QApplication(sys.argv)
    win = MyWindow()
    win.Connect()  # automatically connect to Arduino and MSFS
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    window()  # start the Gui