import socket
import threading
import time

import zmq
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup

from Utils import *

from ZMQClient import ZmqClient
from MainWindow import Ui_MainWindow

class SOAGui(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.gear_group = QButtonGroup(self)
        self.gear_group.addButton(self.Gear_P, 0)
        self.gear_group.addButton(self.Gear_R, 1)
        self.gear_group.addButton(self.Gear_N, 2)
        self.gear_group.addButton(self.Gear_D, 3)
        self.gear_group.buttonClicked[int].connect(self.handle_button_group)

    def handle_button_group(self, idx):
        print(f"{idx} is click")
        if set_gear(idx) is False:
            print("Gear set failed!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    SOA_GUI = SOAGui()
    SOA_GUI.show()
    sys.exit(app.exec_())
# set_gear(1)
# time.sleep(3)
# set_gear(2)
# time.sleep(3)
# set_gear(3)
# time.sleep(3)
