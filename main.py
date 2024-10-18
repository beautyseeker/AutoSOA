import json
import os.path
import time

from PIL.ImageCms import Flags
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup
from charset_normalizer import detect

from SignalWidget import MainWindow
from Utils import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    SOA_GUI = MainWindow()
    SOA_GUI.show()
    sys.exit(app.exec_())
