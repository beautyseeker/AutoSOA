import sys

from PyQt5.QtCore import Qt, QRect, QFileSelector
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import QWidget, QComboBox, QRadioButton, QSlider, QApplication, QSizePolicy, QLineEdit, \
    QHBoxLayout, QLabel, QPushButton, QFileDialog, QButtonGroup, QMessageBox, QAbstractButton, QMainWindow, QVBoxLayout, \
    QListWidget, QTabWidget

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
                'sig_val_field': {'soa_field': {'DoorOpenStatus.pwr_door_sts[{}].pwd_posn':'{}'}, 'min': 0, 'max': 100}
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
                'sig_val_field': {'soa_field': {'WinStsInfo.win_status_info[{}].win_open_value':'{}'}, 'min': 0, 'max': 100},
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
                'sig_sts_enum': {'开启': 2, '关闭': 1},
                'sig_sts_field': {'PlgStatus.tr_ajar_sts':'{}'},
                'sig_val_field': {'soa_field': {'PlgStatus.tr_ajar_sts':'{}'}, 'min': 0, 'max': 100},
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
                'sig_sts_field': {'ChrgrGateWorkStatus.chrgr_port_ajar_sts':'{}',
                                    'ChrgrGateWorkStatus.chrgr_gate_cur_movmt_sts':'{}',
                                    'ChrgrGateWorkStatus.chrgr_gate_pre_movmt_sts':'{}'},
                'sig_val_field': {},
            }
        }


class SignalWidget(QWidget):
    def __init__(self, sig_cfg_dict = None):
        super().__init__()
        self.button_group = None
        self.init_dict = sig_cfg_dict
        self.sig_name = None
        self.sig_enum_button = None
        self.sig_area_comboBox = None
        self.val_slider = None
        self.val_edit = None
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.init_ui()

        self.create_signal_name()
        self.create_signal_area_comboBox()
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


    def send_signal_stat(self, selected_btn: QAbstractButton):
        stat = self.button_group.id(selected_btn)
        area = 0
        if self.sig_area_comboBox is not None:
            area = self.sig_area_comboBox.currentIndex()
            if area < 0:
                self.button_group.setExclusive(False)
                selected_btn.setChecked(False)
                self.button_group.setExclusive(True)
                return
        soa_dict = self.init_dict['soa_dict']
        temp_dict = {key.format(area): int(val.format(stat)) for key,val in self.init_dict['ui_cfg_dict']['sig_sts_field'].items()}
        soa_dict['data'] = temp_dict
        soa.send_data(**soa_dict)

    def send_signal_val(self):
        area = self.sig_area_comboBox.currentIndex()
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
            for key, val in self.init_dict['ui_cfg_dict']['sig_area_enum'].items():
                self.sig_area_comboBox.addItem(key, val)
            self.layout.addWidget(self.sig_area_comboBox)

    def value_confirm(self):
        edit_val = self.val_edit.text()
        if not edit_val.isdigit():
            QMessageBox.warning(self, '输入错误!', f'信号{self.sig_name}输入错误,请重新输入!')
        self.val_slider.setValue(int(edit_val))


class MsgBox(QMessageBox):
    def __init__(self, parent=None):
        super(MsgBox, self).__init__(parent)



class CarSignalTab(QWidget):

    def __init__(self):
        super().__init__()
        self.signal_category = self.init_signal_category()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.signal_category)
        self.layout.addWidget(SignalWidget(door_dict))
        self.layout.addWidget(SignalWidget(window_dict))
        self.layout.addWidget(SignalWidget(handle_dict))
        self.layout.addWidget(SignalWidget(hood_dict))

        self.setLayout(self.layout)

    def init_signal_category(self) -> QComboBox:
        self.signal_category = QComboBox(self)
        self.signal_category.addItems(['信号类别1', '信号类别2'])
        self.signal_category.currentIndexChanged.connect(self.refresh_signal_page)
        return self.signal_category

    def refresh_signal_page(self, selected_signal_category):
        """根据所选信号类别刷新信号UI列表"""
        pass

class AutoRoutinePage(QWidget):
    def __init__(self):
        super().__init__()
        single_line_layout = QHBoxLayout()

        self.file_path_edit = QLineEdit(self)
        self.file_button = QPushButton(self)
        self.file_button.setText('选择路径')

        single_line_layout.addWidget(self.file_button)
        single_line_layout.addWidget(self.file_path_edit)
        self.setLayout(single_line_layout)
        self.file_button.clicked.connect(self.show_file_dialog)

    def show_file_dialog(self):
        file_dir = QFileDialog.getExistingDirectory(None, '回放文件夹','C:/')
        self.file_path_edit.setText(file_dir)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tab_widget = QTabWidget(self)
        self.tab_layout = QVBoxLayout()
        car_sig_tab = CarSignalTab()
        auto_scripts_tab = AutoRoutinePage()
        self.tab_widget.addTab(car_sig_tab, "外部车控信号")
        self.tab_widget.addTab(auto_scripts_tab, "自动化脚本")
        self.setCentralWidget(self.tab_widget)



app = QApplication(sys.argv)
SOA_GUI =  MainWindow()
SOA_GUI.show()
sys.exit(app.exec_())