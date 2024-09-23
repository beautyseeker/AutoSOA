# -*- coding: utf-8 -*-
import typing


from PyQt5 import QtCore, QtGui, QtWidgets

import ZMQClient
from Utils import get_door_handle_stat
from ZMQClient import ZmqClient


class SwitchSignalListItem(QtWidgets.QListWidgetItem):
    """
    用于发送开关信号的Item按钮，点击后可发送SOA信号，反转信号状态和Item样式
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QtGui.QFont("Alibaba PuHuiTi", 12))
        self.default_bg = self.background()
        self.signal_name = self.text()
        self.is_on = False
        self.setForeground(QtGui.QBrush(QtGui.QColor('gray')))

    def click(self, area=None):
        print(f"Area Id:{area}")
        self.is_on = ~self.is_on
        font_col = self.default_bg if self.is_on else QtGui.QBrush(QtGui.QColor('gray'))
        sgnl_sts_sfx = "已开启" if self.is_on else "已关闭"
        self.setForeground(font_col)
        self.setText(self.signal_name + f'({sgnl_sts_sfx})')
        print(f'{self.text()} : {self.is_on}')


class SwitchSignalListArea(QtWidgets.QListWidget):
    """
    用于容纳开关信号的List Widgets区域
    """
    def __init__(self, *args, size=QtCore.QRect(), signal_list=None, bind_choice = None, **kwargs, ):
        super().__init__(*args, **kwargs)
        if bind_choice is not None:
            bind_choice.bind_signal_list = self
        self.bind_choice = bind_choice
        self.itemClicked.connect(self.clicked)
        self.setGeometry(size)
        self.addItems(signal_list)

    def clicked(self, item: SwitchSignalListItem):
        if self.bind_choice is not None:
            item.click(self.bind_choice.currentIndex())
        else:
            item.click()

    def addItems(self, labels: typing.Iterable[str]) -> None:
        for text in labels:
            switch_item = SwitchSignalListItem(text)
            super(SwitchSignalListArea, self).addItem(switch_item)

    def addItem(self, aitem: SwitchSignalListItem) -> None:
        super().addItem(aitem)

    # def update_signal_stat_style(self, area: int):




class AreaChoice(QtWidgets.QComboBox):
    """
    区域选择下拉框
    """
    def __init__(self,*args, size=None, choice_list=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.bind_signal_list = None
        self.check_box_font = QtGui.QFont("Alibaba PuHuiTi", 18)
        self.setFont(self.check_box_font)
        self.setEditable(True)
        self.setGeometry(size)
        self.addItems(choice_list)
        self.currentIndexChanged.connect(self.update_bind_signal_stat)


    def update_bind_signal_stat(self):
        """根据Area Id获取当前ID下的车控信号状态,并更新GUI信号状态"""
        if self.bind_signal_list is not None:
            stat_list = get_door_handle_stat()





class Rotatable(object):
    conor_area = ['左前', '右前', '左后', '右后']
    conor_area_signals = ["车门", "车窗", "把手"]

    aside_area = ['左侧', '右侧']
    aside_area_signal = ["后视镜"]

    other_area_signals = ['前盖', '后盖', '充电盖', '雨刮']

    def __init__(self):
        self.side_area_choice = None
        self.conor_area_choice = None
        self.other_signal_choice = None
        self.other_signal_list = None
        self.aside_signal_list = None
        self.conor_signal_list = None


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        check_box_font = QtGui.QFont()
        check_box_font.setFamily("Alibaba PuHuiTi")
        check_box_font.setPointSize(18)

        # 四角信号UI定义
        self.conor_area_choice = AreaChoice(self.centralwidget, size=QtCore.QRect(40,130,191,51),
                                            choice_list=Rotatable.conor_area)  # 区域下拉框

        self.conor_signal_list = SwitchSignalListArea(self.centralwidget, size=QtCore.QRect(40, 180, 121, 121),
                                                      signal_list=Rotatable.conor_area_signals,bind_choice=self.conor_area_choice)


        # 两侧信号UI定义
        self.side_area_choice = AreaChoice(self.centralwidget, size=QtCore.QRect(250, 130, 191, 51),
                                            choice_list=Rotatable.aside_area)  # 区域下拉框

        self.conor_signal_list = SwitchSignalListArea(self.centralwidget, size=QtCore.QRect(250, 180, 121, 121),
                                                      signal_list=Rotatable.aside_area_signal,bind_choice=self.side_area_choice)

        # 其他信号UI定义
        self.other_signal_choice = QtWidgets.QPushButton(self.centralwidget)
        self.other_signal_choice.setGeometry(QtCore.QRect(480, 130, 191, 51))
        self.other_signal_choice.setFont(check_box_font)

        self.other_signal_list = SwitchSignalListArea(self.centralwidget, size=QtCore.QRect(480, 180, 121, 192),
                                                      signal_list=Rotatable.other_area_signals)


        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        self.other_signal_choice.setText(_translate("MainWindow", "其他信号"))
        self.conor_area_choice.setCurrentText(_translate("MainWindow", "选择区域(四角)"))
        self.side_area_choice.setCurrentText(_translate("MainWindow", "选择区域(两侧)"))

