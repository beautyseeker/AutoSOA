import socket
import threading
import time

import zmq
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup

from Utils import *

from ZMQClient import ZmqClient
from Rotatable import Rotatable

class SOAGui(QMainWindow, Rotatable):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def handle_button_group(self, idx):
        print(f"{idx} is click")
        if set_gear(idx) is False:
            print("Gear set failed!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    SOA_GUI = SOAGui()
    SOA_GUI.show()
    sys.exit(app.exec_())
