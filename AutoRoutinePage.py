import os.path
import threading
import time
from time import sleep

import requests
import json
from datetime import datetime
import subprocess

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFileDialog, QPushButton, QLineEdit, QVBoxLayout, QMessageBox, \
    QComboBox, QLayout, QLabel
from colorama import Fore

from Utils import detect_log_finish, run_cmd


class ConfigEdit(QWidget):
    def __init__(self, placeholder_txt='', button_txt=None):
        super().__init__()
        self.setFixedHeight(50)
        single_line_layout = QHBoxLayout()
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(placeholder_txt)
        single_line_layout.addWidget(self.line_edit, alignment=Qt.AlignTop)
        if button_txt is not None:
            self.button = QPushButton(self)
            self.button.setText(button_txt)
            single_line_layout.addWidget(self.button,alignment=Qt.AlignTop)
            if button_txt == '选择路径':
                self.button.clicked.connect(self.show_file_dialog)
            elif button_txt == '选择程序':
                self.button.clicked.connect(self.select_exe_dialog)

        self.setLayout(single_line_layout)

    def show_file_dialog(self):
        file_dir = QFileDialog.getExistingDirectory(None, '选择文件夹', 'E:/')
        self.line_edit.setText(file_dir)

    def select_exe_dialog(self):
        exe_dir = QFileDialog.getOpenFileName(None, '选择应用程序', 'E:/')
        self.line_edit.setText(exe_dir[0])

    def __str__(self):
        return self.line_edit.text()


class AutoRoutinePage(QWidget):
    def __init__(self):
        super().__init__()
        self.test_category = None
        self.choice_tip = None
        self.background_thread = None
        self.msg_info_box = None
        self.msg_error_box = None
        self.json_config = {}
        self.VLayout = QVBoxLayout()
        self.upr_exe = ConfigEdit(placeholder_txt='选择你的UPRDesktop路径', button_txt='选择程序')
        self.unity_exe = ConfigEdit(placeholder_txt='选择你的Unity编辑器路径', button_txt='选择程序')
        self.unity_project_path = ConfigEdit(placeholder_txt='选择你的Unity工程路径', button_txt='选择路径')
        if os.path.exists(os.path.join(os.getcwd(), 'AutoConfig.json')):
            self.load_path_config()
        self.build_apk_button = QPushButton("打包并安装UPR测试包", self)
        self.build_apk_button.clicked.connect(self.build_upr_apk)

        self.launch_esd_button = QPushButton("开启ESD场景测试", self)
        self.launch_esd_button.clicked.connect(self.launch_esd_replay)

        self.start_upr_button = QPushButton("执行UPR测试", self)
        self.start_upr_button.clicked.connect(self.start_upr_session)


        self.init_test_category()
        self.VLayout.addWidget(self.choice_tip, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.test_category, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.upr_exe, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.unity_exe,alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.unity_project_path, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.build_apk_button, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.launch_esd_button, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.start_upr_button, alignment=Qt.AlignTop)
        self.setLayout(self.VLayout)

    def init_test_category(self):

        self.choice_tip = QLabel(self)
        self.choice_tip.setText("选择你的自动化测试")
        self.test_category = QComboBox(self)


    def save_path_config(self):
        self.json_config["unity_exe"] = self.unity_exe.__str__()
        self.json_config["upr_exe"] = self.upr_exe.__str__()
        self.json_config["unity_project_path"] = self.unity_project_path.__str__()
        with open(r'AutoConfig.json', 'w', encoding='utf-8') as json_file:
            json.dump(self.json_config, json_file, ensure_ascii=False, indent=4)

    def load_path_config(self):
        with open(r'AutoConfig.json', 'r', encoding='utf-8') as json_file:
            self.json_config = json.load(json_file)
            self.unity_exe.line_edit.setText(self.json_config.get("unity_exe"))
            self.unity_project_path.line_edit.setText(self.json_config.get("unity_project_path"))
            self.upr_exe.line_edit.setText(self.json_config.get("upr_exe"))


    def build_upr_apk(self):
        output_log_path = r'E:/log/BuildOutputLog.txt'
        finish_keyword = 'Exiting without the bug reporter. Application will terminate with return code 0'

        unity_build_cmd = (rf"{self.unity_exe} -quit -batchmode -projectPath {self.unity_project_path} "
                           f"-executeMethod ExportAndroidTool.BuildUprAPK -logFile {output_log_path}")

        result = run_cmd('tasklist | findstr Unity.exe', "存在Unity进程", "无Unity进程无需终止")
        if result.returncode == 0:
            # 命令行执行构建前必须终止已存在的Unity进程
            run_cmd(f"taskkill /f /im Unity.exe", "已有Unity进程已终止", "已有Unity进程终止失败")

        self.build_apk_button.setEnabled(False)
        run_cmd(unity_build_cmd, "APK构建完成", "APK构建失败", block=False)
        def async_log_detect():
            detect_log_finish(output_log_path, finish_keyword, self.build_succeed_action)
            """执行出包命令后，后台异步线程不断检查log路径是否生成了最新的Log文件,生成后再执行后续步骤"""
            prim_log_modify_timestamp = os.path.getmtime(output_log_path)
            begin_build_timestamp = time.time()
            timeout = 10
            while time.time() - begin_build_timestamp < timeout:
                current_log_modify_timestamp = os.path.getmtime(output_log_path)
                if current_log_modify_timestamp - prim_log_modify_timestamp > 0.1:
                    print("最新日志已生成，开启日志关键字监测")
                    detect_log_finish(output_log_path, finish_keyword, self.build_succeed_action)
                    return
                time.sleep(0.5)
            print('日志生成超时,流程终止！检查build流程正确性后重试')
        self.background_thread = threading.Thread(target=async_log_detect)
        self.background_thread.start()

    def build_succeed_action(self):
        self.msg_info_box = QMessageBox.information(self, '通知', f'APK包构建完成！')
        build_apk_path = os.path.join(fr'{self.unity_project_path}', "BUILD-APK",
                                      "launcher", "build", "outputs", "apk", "release", "launcher-release.apk")
        if os.path.exists(build_apk_path):
            parent_dir = os.path.dirname(build_apk_path)
            os.startfile(parent_dir)
            apk_push_cmd = f'adb install -r -t {build_apk_path}'
            print("pushing apk...please wait")
            run_cmd(apk_push_cmd, 'APK安装完成!', 'APK安装失败！', timeout=10)
            print(f"推包完成:{build_apk_path}")
        else:
            print(f"推包失败!路径:{build_apk_path}不存在")

    def launch_esd_replay(self):
        def async_launch_esd_replay():
            esd_py_path = r"ESDDataReplay.py"
            self.launch_esd_button.setEnabled(False)
            run_cmd(f'python {esd_py_path}', block=False)
        self.background_thread = threading.Thread(target=async_launch_esd_replay)
        self.background_thread.start()


    def start_upr_session(self, checked,record_duration=30):
        """开始执行UPR测试,前置条件为adb已连接,所测Unity进程已经启动"""
        print("开始执行UPR测试")
        api_endpoint = "http://10.132.134.40/open-api/sessions"
        auth_header = "Basic dWR4RHMwZnFpN0poT0ljbU9qUnFMb2haWkdSUnd0a1g6VFpjcjNIR1RCUFZBdXZPTHRudDlUbTN6ajkyZ0xiTWU="

        # Generate current timestamp in the format YYYYMMDDHHMM
        timestamp = datetime.now().strftime("%Y%m%d%H%M")

        # Create the session name with the timestamp
        session_name = f"metacar-{timestamp}"

        session_request = {
            "AbnormalFrameTimeThreshold": 60,
            "CaptureWebGL": False,
            "EnableADBMemoryCollection": False,
            "EnableAbnormalFrame": False,
            "EnableAutoObjectSnapshot": True,
            "EnableCaptureRenderingThread": True,
            "EnableDeepLua": False,
            "EnableDeepMono": True,
            "EnableOverdrawMonitor": True,
            "EnableOverdrawScreenshot": True,
            "FrameLockEnabled": False,
            "FrameLockFrequency": 30,
            "GCCallStackEnabled": False,
            "GPUProfileEnabled": True,
            "GPUProfileFrequency": 1000,
            "GameName": "metacar",
            "GameVersion": "1",
            "Monitor": False,
            "ObjectSnapshotFrequency": 5,
            "PackageName": "com.nio.metacar",
            "ProjectId": "17b6c10b-389a-4fb5-9158-3a4eb9b3f187",
            "ScreenshotEnabled": True,
            "ScreenshotFrequency": 4,
            "SessionName": session_name,
            "ShareReport": True,
            "Tags": ["string"],
            "UnityVersion": "2022.2"
        }

        # Send POST request
        headers = {
            "accept": "application/json",
            "authorization": auth_header,
            "Content-Type": "application/json"
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(session_request))

        # Print full response
        print("Full response:", response.text)

        # Extract and print SessionId
        try:
            response_json = response.json()
            session_id = response_json.get("SessionId", "SessionId not found")
            print("SessionId:", session_id)
        except json.JSONDecodeError:
            print("Failed to decode JSON response")

        # If session_id is found, execute the next command
        if session_id and session_id != "SessionId not found":
            # Construct the command
            upr_record_cmd = rf"{self.upr_exe} -p 127.0.0.1 -s {session_id} -n com.nio.metacar"

            try:
                def async_upr_record():
                    self.start_upr_button.setEnabled(False)
                    run_cmd(upr_record_cmd, block=False)
                    print("UPRDesktop.exe executed successfully.")
                    print("recording duration:", record_duration)
                    for i in range(record_duration):
                        if i % 5 == 0:
                            print(f'upr recording...{i} sec')
                        time.sleep(1)
                    run_cmd(f'{self.upr_exe} --stop')
                    self.start_upr_button.setEnabled(True)
                self.background_thread = threading.Thread(target=async_upr_record)
                self.background_thread.start()
            except subprocess.CalledProcessError as e:
                self.start_upr_button.setEnabled(True)
                print(f"UPR录制启动错误: {e}")
        else:
            print("No valid SessionId found. UPRDesktop.exe will not be executed.")


class BackThread(QThread):
    output_signal = pyqtSignal()

    def __init__(self, async_action):
        super().__init__()
        self.async_action = async_action

    def run(self):
        self.async_action()
        self.output_signal.emit()

