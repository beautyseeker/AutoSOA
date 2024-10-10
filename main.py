import json

from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup

from SignalWidget import MainWindow
from Utils import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    SOA_GUI = MainWindow()
    SOA_GUI.show()
    sys.exit(app.exec_())
