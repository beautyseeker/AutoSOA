import os.path

import requests
import json
from datetime import datetime
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFileDialog, QPushButton, QLineEdit, QVBoxLayout
from colorama import Fore


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
        self.json_config = {}
        self.VLayout = QVBoxLayout()
        self.upr_exe = ConfigEdit(placeholder_txt='选择你的UPRDesktop路径', button_txt='选择程序')
        self.unity_exe = ConfigEdit(placeholder_txt='选择你的Unity编辑器路径', button_txt='选择程序')
        self.unity_project_path = ConfigEdit(placeholder_txt='选择你的Unity工程路径', button_txt='选择路径')
        if os.path.exists(os.path.join(os.getcwd(), 'AutoConfig.json')):
            self.load_path_config()
        build_apk_button = QPushButton(self)
        build_apk_button.setText("打包生成APK")
        build_apk_button.clicked.connect(self.build_upr_apk)

        start_upr_button = QPushButton(self)
        start_upr_button.setText("执行UPR测试")
        start_upr_button.clicked.connect(self.implement_upr_session)

        self.VLayout.addWidget(self.upr_exe, alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.unity_exe,alignment=Qt.AlignTop)
        self.VLayout.addWidget(self.unity_project_path, alignment=Qt.AlignTop)
        self.VLayout.addWidget(build_apk_button, alignment=Qt.AlignTop)
        self.VLayout.addWidget(start_upr_button, alignment=Qt.AlignTop)
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
        unity_build_cmd = (f"{self.unity_exe} -quit -batchmode -projectPath {self.unity_project_path} "
                           f"-executeMethod ExportAndroidTool.BuildUprAPK -logFile E:log/BuildOutputLog.txt")
        try:
            print(f"Executing: {unity_build_cmd}")
            result = subprocess.run(unity_build_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Command Output:\n{result.stdout.decode()}")
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"An error occurred while pushing: {e.stderr.decode()}")

    def detect_build_finish(self, finish_log="生成成功"):
        pass


    def implement_upr_session(self):
        """开始执行UPR测试,前置条件为adb已连接,所测Unity进程已经启动"""
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
                f'{self.upr_exe}',
                "-p", "127.0.0.1",  # Replace <device_ip> with the actual device IP
                "-s", session_id,
                "-n", "com.nio.metacar"  # Replace with the actual package name if different
            ]

            # Change directory and run the command
            try:
                subprocess.run(command, cwd=os.path.curdir, check=True)
                print("UPRDesktop.exe executed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while executing UPRDesktop.exe: {e}")
        else:
            print("No valid SessionId found. UPRDesktop.exe will not be executed.")
