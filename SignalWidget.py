import sys

from PyQt5.QtCore import Qt, QRect, QFileSelector
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import QWidget, QComboBox, QRadioButton, QSlider, QApplication, QSizePolicy, QLineEdit, \
    QHBoxLayout, QLabel, QPushButton, QFileDialog, QButtonGroup, QMessageBox, QAbstractButton, QMainWindow, QVBoxLayout, \
    QListWidget, QTabWidget

from AutoRoutinePage import AutoRoutinePage
from HVACPage import HVACPage
from Utils import soa

door_dict = {
            'soa_dict':{
                'service': 'DoorOpenMgr',
                'instance_name': '',
                'rpc': 'DoorOpenSts',
                'data': {}
            },
            'ui_cfg_dict':{
                'sig_name': '车门',
                'sig_area_enum': {'左上': 0, '右上': 1, '左下': 2, '右下': 3},
                'sig_sts_enum': {'开启': 2, '关闭': 1},
                'sig_sts_field':{'DoorOpenStatus.door_sts[{}].door_ajar_sts_validity':'1',
                        'DoorOpenStatus.door_sts[{}].door_ajar_sts':'{}'},
                'sig_val_field': {'soa_field': {'DoorOpenStatus.pwr_door_sts[{}].pwd_posn':'{}'},
                                  'min': 0, 'max': 100, 'val_prompt':'电动门开度'},
                'sig_mode_enum':{}
            }
        }

window_dict = {
            'soa_dict':{
                'service': 'WinMgr',
                'instance_name': '',
                'rpc': 'WinSts',
                'data': {}
            },
            'ui_cfg_dict':{
                'sig_name': '车窗',
                'sig_area_enum': {'左上': 0, '右上': 1, '左下': 2, '右下': 3},
                'sig_sts_enum': {'开启': 100, '关闭': 0},
                'sig_sts_field': {'WinStsInfo.win_status_info[{}].win_open_value': '{}'},
                'sig_val_field': {'soa_field': {'WinStsInfo.win_status_info[{}].win_open_value':'{}'},
                                  'min': 0, 'max': 100, 'val_prompt':'车窗百分比开度'},
            }
        }

handle_dict = {
            'soa_dict':{
                'service': 'DoorHndlMgr',
                'instance_name': '',
                'rpc': 'DoorHndlSts',
                'data': {}
            },
            'ui_cfg_dict':{
                'sig_name': '把手',
                'sig_area_enum': {'左上': 0, '右上': 1, '左下': 2, '右下': 3},
                'sig_sts_enum': {'开启': 1, '关闭': 2, '半开': 3},
                'sig_sts_field': {'DoorHndlStatus.side_door_hndl_sts[{}].door_hndl_sts':'{}'},
                'sig_val_field': {},
            }
        }

hood_dict = {
            'soa_dict':{
                'service': 'HoodMgr',
                'instance_name': '',
                'rpc': 'CentHoodSts',
                'data': {}
            },
            'ui_cfg_dict':{
                'sig_name': '前盖',
                'sig_area_enum': {},
                'sig_sts_enum': {'开启': 2, '关闭': 1},
                'sig_sts_field': {'HoodStatus.hood_movmt_sts':'{}',
                                  'HoodStatus.hood_ajar_sts': '{}'},
                'sig_val_field': {},
            }
        }

trunklid_dict = {
            'soa_dict':{
                'service': 'PlgMgr',
                'instance_name': '',
                'rpc': 'CentPlgSts',
                'data': {}
            },
            'ui_cfg_dict':{
                'sig_name': '后盖',
                'sig_area_enum': {},
                'sig_sts_enum': {'开启': 100, '关闭': 0},
                'sig_sts_field': {'PlgStatus.plg_posn':'{}'},
                'sig_val_field': {'soa_field': {'PlgStatus.plg_posn':'{}'},
                                  'min': 0, 'max': 100, 'val_prompt':'尾箱开度'},
            }
        }

charger_dict = {
            'soa_dict':{
                'service': 'ChrgrGateMgr',
                'instance_name': '',
                'rpc': 'ChrgrGateWorkSts',
                'data': {}
            },
            'ui_cfg_dict':{
                'sig_name': '充电盖',
                'sig_area_enum': {},
                'sig_sts_enum': {'开启': 2, '关闭': 1},
                'sig_sts_field': {'ChrgrGateWorkStatus.chrgr_port_ajar_sts':'{}'},
                'sig_val_field': {},
            }
        }

mirror_dict = {
            'soa_dict':{
                'service': 'MirrFoldMgr',
                'instance_name': '',
                'rpc': 'MirrFoldSts',
                'data': {}
            },
            'ui_cfg_dict':{
                'sig_name': '后视镜',
                'sig_area_enum': {'左侧':'left','右侧':'right'},
                'sig_sts_enum': {'展开': 3, '收起': 1},
                'sig_sts_field': {'MirrFoldStsInfo.{}_mirr_fold_sts':'{}'},
                'sig_val_field': {},
            }
        }

wiper_dict = {
            'soa_dict':{
                'service': 'FrontWiperMgr',
                'instance_name': '',
                'rpc': 'FwiperSts',
                'data': {}
            },
            'ui_cfg_dict':{
                'sig_name': '雨刮',
                'sig_area_enum': {},
                'sig_sts_enum': { '关闭': 0,'低速': 2, '高速': 3},
                'sig_sts_field': {'FwiperStatus.f_wiper_work_mod':'{}'},
                'sig_val_field': {},
            }
        }

gear_dict = {
    'soa_dict': {
        'service': 'GearCtrlSrv',
        'instance_name': 'GearCtrlSrvPri',
        'rpc': 'IfGearInfo',
        'data': {}
    },
    'ui_cfg_dict': {
        'sig_name': '挡位',
        'sig_area_enum': {},
        'sig_sts_enum': {'P挡': 0, 'N挡': 1, 'R挡': 2, 'D挡': 3},
        'sig_sts_field': {'GearInfo.display_act_gear': '{}','GearInfo.display_act_gear_vld': 1},
        'sig_val_field': {},
    }
}

car_speed_dict = {

}

car_signal_category_dict = {
    '旋转部件':[
        door_dict,
        window_dict,
        handle_dict,
        hood_dict,
        trunklid_dict,
        charger_dict,
        mirror_dict,
        wiper_dict
    ],
    '行车状态':[
        gear_dict,
    ],
    '外部灯光':[

    ],

    '充放电':[

    ],
    '内外饰配置':[

    ]
}

class SignalConfig:
    class WidgetConfig:
        def __init__(self, sig_name: str, sig_area_enum=None, sig_sts_enum=None, sig_mode_enum=None, sig_val_field=None):
            self.sig_name = sig_name
            self.sig_area_enum = sig_area_enum
            self.sig_sts_enum = sig_sts_enum
            self.sig_mode_enum = sig_mode_enum
            self.sig_val_field = sig_val_field


    def __init__(self, service_name: str, rpc: str, ui_cfg: WidgetConfig, instance_name=''):
        self.soa_dict = {'service': service_name, 'instance_name':instance_name,'rpc': rpc, 'data': {}}
        self.ui_cfg = ui_cfg


class SignalWidget(QWidget):
    def __init__(self, sig_cfg_dict = None):
        super().__init__()
        self.button_group = None
        self.init_dict = sig_cfg_dict
        self.sig_name = None
        self.sig_enum_button = None
        self.sig_area_comboBox = None
        self.sig_mode_comboBox = None
        self.val_slider = None
        self.val_edit = None
        self.setFixedHeight(50)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.init_ui()

        self.create_signal_name()
        self.create_signal_area_comboBox()
        self.create_signal_mode_comboBox()
        self.create_signal_enum_button()
        self.create_signal_value_slider()
        self.create_signal_value_eidt()


    def init_ui(self):
        pal = self.palette()
        self.setAutoFillBackground(True)
        pal.setColor(QPalette.Background, Qt.gray)
        self.setPalette(pal)

    def create_signal_value_slider(self):
        if self.init_dict['ui_cfg_dict']['sig_val_field'].__len__() != 0:
            self.val_slider = QSlider(self)
            self.val_slider.setOrientation(Qt.Horizontal)
            self.val_slider.setMinimum(self.init_dict['ui_cfg_dict']['sig_val_field']['min'])
            self.val_slider.setMaximum(self.init_dict['ui_cfg_dict']['sig_val_field']['max'])
            self.val_slider.sliderReleased.connect(self.send_signal_val)
            self.layout.addWidget(self.val_slider)


    def create_signal_enum_button(self):
        sig_sts_enum = self.init_dict['ui_cfg_dict'].get('sig_sts_enum', None)
        if sig_sts_enum is not None and len(sig_sts_enum) != 0:
            self.button_group = QButtonGroup(self)
            for key ,val in sig_sts_enum.items():
                self.sig_enum_button = QRadioButton(self)
                self.sig_enum_button.setText(key)
                self.button_group.addButton(self.sig_enum_button, val)
                self.layout.addWidget(self.sig_enum_button)
            self.button_group.buttonClicked.connect(self.send_signal_stat)


    def button_group_uncheck(self, btn):
        if self.button_group is not None:
            checked_btn = self.button_group.checkedButton()
            if checked_btn is not None:
                self.button_group.setExclusive(False)
                checked_btn.setChecked(False)
                self.button_group.setExclusive(True)

    def send_signal_stat(self, selected_btn: QAbstractButton):
        stat = self.button_group.id(selected_btn)
        area = 0
        if self.sig_area_comboBox is not None:
            area = self.sig_area_comboBox.currentData()
            if area is None:
                self.button_group.setExclusive(False)
                selected_btn.setChecked(False)
                self.button_group.setExclusive(True)
                return
        soa_dict = self.init_dict['soa_dict']
        temp_dict = {key.format(area): int(val.format(stat)) for key,val in self.init_dict['ui_cfg_dict']['sig_sts_field'].items()}
        soa_dict['data'] = temp_dict
        soa.send_data(**soa_dict)

    def send_signal_val(self):
        area = 0
        if self.sig_area_comboBox is not None:
            area = self.sig_area_comboBox.currentData()
        slider_val = self.val_slider.value()
        self.val_edit.setText(str(slider_val))
        soa_val_field = self.init_dict['ui_cfg_dict']['sig_val_field']['soa_field']
        soa_dict = self.init_dict['soa_dict']
        temp_dict = {key.format(area): int(val.format(slider_val)) for key,val in soa_val_field.items()}
        soa_dict['data'] = temp_dict
        soa.send_data(**soa_dict)

    def create_signal_value_eidt(self):
        if self.init_dict['ui_cfg_dict']['sig_val_field'].__len__() != 0:
            self.val_edit = QLineEdit(self)
            self.val_edit.setPlaceholderText(str(self.init_dict['ui_cfg_dict']['sig_val_field'].get('val_prompt', None)))
            self.val_edit.returnPressed.connect(self.value_confirm)
            self.layout.addWidget(self.val_edit)

    def create_signal_name(self):
        self.sig_name = QLabel(self)
        self.sig_name.setText(self.init_dict['ui_cfg_dict'].get('sig_name', ''))
        self.sig_name.setFont(QFont('Alibaba PuHuiTi', 14, QFont.Bold))
        self.layout.addWidget(self.sig_name)

    def create_signal_area_comboBox(self):
        sig_area_enum = self.init_dict['ui_cfg_dict'].get('sig_area_enum', None)
        if sig_area_enum is not None and self.init_dict['ui_cfg_dict']['sig_area_enum'].__len__() != 0:
            self.sig_area_comboBox = QComboBox(self)
            self.sig_area_comboBox.currentIndexChanged.connect(self.button_group_uncheck)
            for key, val in self.init_dict['ui_cfg_dict']['sig_area_enum'].items():
                self.sig_area_comboBox.addItem(key, val)
            self.layout.addWidget(self.sig_area_comboBox)

    def create_signal_mode_comboBox(self):
        sig_mode_enum = self.init_dict['ui_cfg_dict'].get('sig_mode_enum', None)
        if sig_mode_enum is not None and self.init_dict['ui_cfg_dict']['sig_mode_enum'].__len__() != 0:
            self.sig_mode_comboBox = QComboBox(self)
            for key, val in self.init_dict['ui_cfg_dict']['sig_mode_enum'].items():
                self.sig_mode_comboBox.addItem(key, val)
            self.layout.addWidget(self.sig_mode_comboBox)

    def value_confirm(self):
        edit_val = self.val_edit.text()
        if not edit_val.isdigit():
            QMessageBox.warning(self, '输入错误!', f'信号{self.sig_name}输入错误,请重新输入!')
        self.val_slider.setValue(int(edit_val))

class CarSignalTab(QWidget):

    def __init__(self):
        super().__init__()
        self.signal_widget_list = None
        self.QSignal_list = []
        self.layout = QVBoxLayout()
        self.signal_category = self.init_signal_category()

        self.setLayout(self.layout)

    def init_signal_category(self) -> QComboBox:
        self.signal_category = QComboBox(self)
        self.signal_category.setObjectName("signal_category")
        self.signal_category.addItems(car_signal_category_dict.keys())
        self.layout.addWidget(self.signal_category, alignment=Qt.AlignTop)
        self.signal_category.setCurrentIndex(0)
        self.refresh_signal_page(self.signal_category.currentText())
        self.signal_category.currentTextChanged.connect(self.refresh_signal_page)


    def refresh_signal_page(self, selected_signal_category):
        """根据所选信号类别刷新信号UI列表"""
        if self.QSignal_list is not None:
            for Qsignal in self.QSignal_list:
                self.layout.removeWidget(Qsignal)
                Qsignal.deleteLater()
            self.QSignal_list.clear()

        self.signal_widget_list = car_signal_category_dict.get(selected_signal_category, None)
        if self.signal_widget_list is not None:
            for signal_widget in self.signal_widget_list:
                Qsignal = SignalWidget(signal_widget)
                self.layout.addWidget(Qsignal, alignment=Qt.AlignTop)
                self.QSignal_list.append(Qsignal)
        self.adjustSize()


class CarStylePage(QWidget):
    def __init__(self):
        super().__init__()
        single_line_layout = QHBoxLayout()
        self.setLayout(single_line_layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoSOA")
        self.tab_widget = QTabWidget(self)
        self.tab_layout = QVBoxLayout()
        self.car_sig_tab = CarSignalTab()
        self.auto_scripts_tab = AutoRoutinePage()
        self.hvac_tab = HVACPage()
        self.car_style_cfg_tab = CarStylePage()
        self.tab_widget.addTab(self.car_sig_tab, "外部车控信号")
        self.tab_widget.addTab(self.car_style_cfg_tab, "内外饰配置")
        self.tab_widget.addTab(self.hvac_tab, "HVAC")
        self.tab_widget.addTab(self.auto_scripts_tab, "自动化脚本")
        self.setCentralWidget(self.tab_widget)

    def closeEvent(self, a0):
        self.auto_scripts_tab.save_path_config()