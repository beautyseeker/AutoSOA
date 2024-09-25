# -*- coding: utf-8 -*-
import typing
import itertools


from PyQt5 import QtCore, QtGui, QtWidgets

from Utils import get_door_handle_stat, get_conor_signal_group, set_door_stat, set_door_handle_stat, set_window_stat, \
    set_hood_stat, set_trunk_lid_stat, set_charger_stat, set_mirror_stat


class SwitchSignalListItem(QtWidgets.QListWidgetItem):
    """
    用于发送开关信号的Item按钮，点击后可发送SOA信号，反转信号状态和Item样式
    """

    def __init__(self, *args, signal_info=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QtGui.QFont("Alibaba PuHuiTi", 12))
        self.default_bg = self.background()
        self.signal_name = self.text()
        self.signal_set_call = signal_info['signal_set_call']
        self.signal_stat_enum_cycle = itertools.cycle(signal_info['sig_sts'].items())
        self.stat_val = -1
        self.setForeground(QtGui.QBrush(QtGui.QColor('gray')))


    def click(self, area=None):
        """根据当前Item的名字、当前选中is_on信号状态(再映射回stat值)、选取不同的设置信号方法"""
        print(f"Area Id:{area}")
        key, value = next(self.signal_stat_enum_cycle)
        if area is None:
            self.signal_set_call(stat=value)
        else:
            self.signal_set_call(area=area, stat=value)
        self.update_prompt(key)


    def update_prompt(self, sts_enum):
        self.setText(self.signal_name + f'{sts_enum}')
        print(f'{self.text()} : {sts_enum}')


class SwitchSignalListArea(QtWidgets.QListWidget):
    """
    用于容纳开关信号的List Widgets区域
    """
    mapping_rule_dict = {'车门': {'sig_sts':{'on':2, 'off':1}, 'signal_set_call': set_door_stat, 'bind_item': None},
                         '车窗': {'sig_sts':{'on':100, 'off':0}, 'signal_set_call': set_window_stat, 'bind_item': None},
                         '把手': {'sig_sts':{'on':1, 'off':2, 'half':3}, 'signal_set_call': set_door_handle_stat, 'bind_item': None},
                         '前盖': {'sig_sts':{'on':2, 'off':1}, 'signal_set_call': set_hood_stat, 'bind_item': None},
                         '后视镜': {'sig_sts':{'on':1, 'off':3}, 'signal_set_call': set_mirror_stat, 'bind_item': None},
                         '后盖': {'sig_sts':{'on':2, 'off':1}, 'signal_set_call': set_trunk_lid_stat, 'bind_item': None},
                         '充电盖': {'sig_sts':{'on':2, 'off':1}, 'signal_set_call': set_charger_stat, 'bind_item': None},
                         '雨刮': {'sig_sts':{'on':0, 'off':1}, 'signal_set_call': set_hood_stat, 'bind_item': None}}

    def __init__(self, *args, size=QtCore.QRect(), signal_list=None, bind_choice = None, **kwargs, ):
        super().__init__(*args, **kwargs)
        if bind_choice is not None:
            bind_choice.bind_QListWidget = self
        self.bind_choice = bind_choice
        self.itemClicked.connect(self.clicked)
        self.signal_stat_dict = SwitchSignalListArea.mapping_rule_dict
        self.setGeometry(size)
        self.addItems(signal_list)

    def clicked(self, item: SwitchSignalListItem):
        if self.bind_choice is not None:
            item.click(self.bind_choice.currentIndex())
        else:
            item.click()

    def addItems(self, labels: typing.Iterable[str]) -> None:
        for text in labels:
            switch_info = self.signal_stat_dict[text]
            switch_item = SwitchSignalListItem(text, signal_info=switch_info)
            super(SwitchSignalListArea, self).addItem(switch_item)
            self.signal_stat_dict[text]['bind_item'] = switch_item


    def addItem(self, aitem: SwitchSignalListItem) -> None:
        super().addItem(aitem)
        self.signal_stat_dict[aitem.signal_name]['bind_item'] = aitem

    def update_signal_stat_style(self, stat_dict: typing.Dict[str, int]) -> None:
        """根据获取到一组信号状态来设置ListItem的样式"""
        for key, value in stat_dict.items():
            sig_sts_dict = self.signal_stat_dict[key]['sig_sts']
            for enum_key, sig_val in sig_sts_dict.items():
                if value == sig_val:
                    self.signal_stat_dict[key]['bind_item'].update_prompt(enum_key)
                    break


class AreaChoice(QtWidgets.QComboBox):
    """
    区域选择下拉框
    """
    def __init__(self,*args, size=None, choice_list=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.bind_QListWidget = None
        self.check_box_font = QtGui.QFont("Alibaba PuHuiTi", 18)
        self.setFont(self.check_box_font)
        self.setEditable(True)
        self.setGeometry(size)
        self.addItems(choice_list)
        self.setCurrentIndex(-1)
        self.currentIndexChanged.connect(self.update_bind_signal_stat)


    def update_bind_signal_stat(self, area_index):
        """根据Area Id获取当前Conor下的车控信号状态,并更新该组信号列表状态"""
        if self.bind_QListWidget is not None:
            stat_dict = get_conor_signal_group(area_index)
            self.bind_QListWidget.update_signal_stat_style(stat_dict)


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

