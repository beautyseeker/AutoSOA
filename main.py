import json
import os.path
import time

from PIL.ImageCms import Flags
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup
from charset_normalizer import detect

from SignalWidget import MainWindow
from Utils import *
# from statr_upr_record import command

def push_upr_apk():
    build_apk_path = os.path.join(r"E:\\NT3DOM\\autodrivinghmi\\projects\\main_project", "BUILD-APK", "launcher", "build", "outputs", "apk",
                                  "release", "launcher-release.apk")
    if os.path.exists(build_apk_path):
        os.startfile(os.path.dirname(build_apk_path))
        apk_push_cmd = f'adb install -r -t {build_apk_path}'
        print("pushing apk...please wait")
        res = subprocess.Popen(["powershell", "-Command", apk_push_cmd], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        res.communicate()
        print(f"推包完成:{build_apk_path}")


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # SOA_GUI = MainWindow()
    # SOA_GUI.show()
    # sys.exit(app.exec_())
    output_log_path = r'E:\log\BuildOutputLog.txt'
    finish_keyword = 'Exiting without the bug reporter. Application will terminate with return code 0'
    unity_build_cmd = rf"E:\UnityHub\2022.3.14f1c1\Editor\Unity.exe -quit -batchmode -projectPath E:\NT3DOM\autodrivinghmi\projects\main_project -executeMethod ExportAndroidTool.BuildUprAPK -logFile {output_log_path}"
    # run_cmd(unity_build_cmd, block=False)
    # time.sleep(2)
    detect_log_finish(output_log_path, finish_keyword, push_upr_apk)

    time.sleep(2)
    subprocess.run(['python', r'E:\ProjectsDir\PyCharmDir\quick_verify\ESDDataReplay.py'])
    time.sleep(2)
    subprocess.run(['python', r'E:\ProjectsDir\PyCharmDir\quick_verify\start_upr_record.py'])


