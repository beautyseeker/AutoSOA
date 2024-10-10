from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QVBoxLayout, QComboBox
import SignalWidget

hvac_power_dict = {
    'soa_dict': {
        'service': 'CbnClmtMgr',
        'instance_name': '',
        'rpc': 'HvacOnOffSts',
        'data': {}
    },
    'ui_cfg_dict': {
        'sig_name': '空调开关',
        'sig_area_enum': {'第一排': 'hvac_', '第二排': 'sec_','主驾': 'frnt_le_', '副驾': 'frnt_ri_'},
        'sig_sts_enum': {'开启': 1, '关闭': 0},
        'sig_sts_field': {'HvacOnOffStatus.{}on_off_sts': '{}'},
        'sig_val_field': {},
        'sig_mode_enum': {}
    }
}

condition_temp_dict = {
    'soa_dict': {
        'service': 'CbnClmtMgr',
        'instance_name': '',
        'rpc': 'HvacTempSts',
        'data': {}
    },
    'ui_cfg_dict': {
        'sig_name': '空调温度',
        'sig_area_enum': {'第一排': '', '第二排': 'sec_', '主驾': 'frnt_le_', '副驾': 'frnt_ri_'},
        'sig_sts_enum': {},
        'sig_sts_field': {'HvacTempStatus.{}temp': '{}'},
        'sig_val_field': {'soa_field': {'HvacTempStatus.{}_temp': '{}'},
                                  'min': 15, 'max': 31, 'step':0.5,'val_prompt':'摄氏度'},
        'sig_mode_enum': {}
    }
}

fan_speed_dict = {
    'soa_dict': {
        'service': 'CbnClmtMgr',
        'instance_name': '',
        'rpc': 'HvacBlwSts',
        'data': {}
    },
    'ui_cfg_dict': {
        'sig_name': '空调风量',
        'sig_area_enum': {'第一排': '', '第二排': 'sec_', '主驾': 'frnt_le_', '副驾': 'frnt_ri_'},
        'sig_sts_enum': {},
        'sig_sts_field': {'HvacBlwStatus.{}blw_lvl': '{}'},
        'sig_val_field': {'soa_field':{'HvacBlwStatus.{}blw_lvl': '{}'},
                                  'min': 0, 'max': 8, 'step':1, 'val_prompt':'风量挡位'},
        'sig_mode_enum': {}
    }
}


class HVACPage(QWidget):
    def __init__(self):
        super().__init__()
        self.signal_category = self.init_signal_category()
        single_line_layout = QVBoxLayout()
        single_line_layout.addWidget(self.signal_category, alignment=Qt.AlignTop)
        single_line_layout.addWidget(SignalWidget.SignalWidget(hvac_power_dict))
        single_line_layout.addWidget(SignalWidget.SignalWidget(condition_temp_dict))
        single_line_layout.addWidget(SignalWidget.SignalWidget(fan_speed_dict))
        self.setLayout(single_line_layout)

    def init_signal_category(self) -> QComboBox:
        self.signal_category = QComboBox(self)
        self.signal_category.addItems(['空调', '座椅', '氛围'])
        self.signal_category.currentIndexChanged.connect(self.refresh_signal_page)
        return self.signal_category

    def refresh_signal_page(self):
        pass

