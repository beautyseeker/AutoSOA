import os.path
import threading
import time

import requests
import json
from datetime import datetime
import subprocess

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFileDialog, QPushButton, QLineEdit, QVBoxLayout, QMessageBox
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
        self.stop_thread = None
        self.log_detect_thread = None
        self.msg_info_box = None
        self.msg_error_box = None
        self.json_config = {}
        self.VLayout = QVBoxLayout()
        self.upr_exe = ConfigEdit(placeholder_txt='选择你的UPRDesktop路径', button_txt='选择程序')
        self.unity_exe = ConfigEdit(placeholder_txt='选择你的Unity编辑器路径', button_txt='选择程序')
        self.unity_project_path = ConfigEdit(placeholder_txt='选择你的Unity工程路径', button_txt='选择路径')
        if os.path.exists(os.path.join(os.getcwd(), 'AutoConfig.json')):
            self.load_path_config()
        self.build_apk_button = QPushButton("打包生成APK", self)
        self.build_apk_button.clicked.connect(self.build_upr_apk)

        self.start_upr_button = QPushButton("执行UPR测试", self)
        self.start_upr_button.clicked.connect(self.start_upr_session)

        self.VLayout.addWidget(self.upr_exe, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.unity_exe,alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.unity_project_path, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.build_apk_button, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.start_upr_button, alignment=Qt.AlignTop)
        self.setLayout(self.VLayout)

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
        output_log_path = r'E:log/BuildOutputLog.txt'
        finish_keyword = 'Exiting without the bug reporter. Application will terminate with return code 0'
        unity_build_cmd = (rf"{self.unity_exe} -quit -batchmode -projectPath {self.unity_project_path} "
                           f"-executeMethod ExportAndroidTool.BuildUprAPK -logFile {output_log_path}")

        result = run_cmd('tasklist | findstr Unity.exe', "存在Unity进程", "无Unity进程无需终止")
        if result.returncode == 0:
            # 命令行执行构建前必须终止已存在的Unity进程
            run_cmd(f"taskkill /f /im Unity.exe", "已有Unity进程已终止", "已有Unity进程终止失败")

        self.build_apk_button.setEnabled(False)
        run_cmd(unity_build_cmd, "APK构建完成", "APK构建失败", block=False)
        # 启用log监听，检测到完成关键字后执行推包
        detect_log_finish(output_log_path, finish_keyword, self.build_succeed_action)

    def build_succeed_action(self):
        self.msg_info_box = QMessageBox.information(self, '通知', f'APK包构建完成！')
        build_apk_path = os.path.join(self.unity_project_path, "BUILD-APK", "launcher", "build", "outputs", "apk",
                                      "release", "launcher-release.apk")
        if os.path.exists(build_apk_path):
            parent_dir = os.path.dirname(build_apk_path)
            os.startfile(parent_dir)
            apk_push_cmd = f'adb push -r -t -d {build_apk_path}'
            res = run_cmd(apk_push_cmd, 'APK安装完成!', 'APK安装失败！', block=False)
            if res.returncode == 0:
                self.msg_info_box = QMessageBox.information(self, '通知!', f'APK包安装完成！')
        else:
            QMessageBox.warning(self, '错误!', f"推包失败!路径:{build_apk_path}不存在")


    def stop_upr_recording(self, rcd_dur=60):
        time.sleep(rcd_dur)
        run_cmd(f'{self.upr_exe} --stop')


    def start_upr_session(self, record_duration=30):
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
            command = [
                rf'{self.upr_exe}',
                "-p", "127.0.0.1",  # Replace <device_ip> with the actual device IP
                "-s", session_id,
                "-n", "com.nio.metacar"  # Replace with the actual package name if different
            ]

            # Change directory and run the command
            try:
                self.stop_thread = threading.Thread(target=self.stop_upr_recording)
                self.stop_thread.start()
                subprocess.run(command, cwd=os.path.curdir, check=True)
                print("UPRDesktop.exe executed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while executing UPRDesktop.exe: {e}")
        else:
            print("No valid SessionId found. UPRDesktop.exe will not be executed.")


class CMDThread(QThread):
    output_signal = pyqtSignal()

    def __init__(self, async_action):
        super().__init__()
        self.async_action = async_action

    def run(self):
        self.async_action()

