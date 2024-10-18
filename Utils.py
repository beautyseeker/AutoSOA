import subprocess
import sys
import time
from subprocess import CompletedProcess
from typing import Callable, Union

from PyQt5.QtWidgets import QMessageBox
from colorama import init, Fore
from enum  import IntEnum, Enum

from ZMQClient import ZmqClient


soa = ZmqClient()

class AppSimplifiedName(Enum):
    ESD = 'com.nio.metacar',
    SIG_PAGE = 'com.nextev.account'

    def __str__(self):
        return self.value

def is_dir_exists_on_device(path):
    try:
        # 使用 adb shell ls 命令检查路径是否存在
        result = subprocess.run(
            ["adb", "shell", "ls", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        print(result.stdout)

        # 如果路径不存在，ls 命令会返回错误信息
        if b"No such file or directory" in result.stderr:
            print(f"路径 {path} 不存在")
            return False
        else:
            print(f"路径 {path} 存在")
            return True
    except Exception as e:
        print(f"发生错误: {e}")
        return False


@staticmethod
def is_adb_device_connect() -> bool:
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        output = result.stdout.splitlines()
        devices = [line for line in output if "device" in line and not line.startswith("List") and "offline" not in line]
        if devices:
            return True
        else:
            return False
    except Exception as e:
        print(f"运行 adb devices 时出错: {e}")
        return False


def is_app_running_ps(package_name):
    try:
        # 使用 adb shell ps 命令列出进程
        result = subprocess.run(
            ["adb", "shell", "ps"],
            capture_output=True, text=True
        )
        # 检查包名是否在进程列表中
        if package_name in result.stdout:
            print(f"应用 {package_name} 已启动")
            return True
        else:
            print(f"应用 {package_name} 未启动")
            return False
    except Exception as e:
        print(f"运行adb shell ps发生错误: {e}")
        return False

def is_ZMQ_available() -> bool:
    pass


def wait_until(condition: Callable[..., bool], *args,  interval=2, timeout=150, delay_wait=0, callback=None, **kwargs,):
    start = time.time()
    while condition(*args, **kwargs) == False and time.time() - start < timeout:
        time.sleep(interval)
    if time.time() - start > timeout:
        print("TimeOut!")
        sys.exit(-1)
    print("condition met!")
    time.sleep(delay_wait)
    if callback is not None:
        callback()

def run_cmd(cmd: str, success_prompt='', failed_prompt='', block=True, timeout=5):
    try:
        print(f"running cmd: {cmd}")
        if block:
            cmd_progress = subprocess.run(cmd, shell=True, text=True, timeout=timeout)
            if cmd_progress.returncode == 0:
                print(success_prompt)
                # if MainWindow.instance is not None:
                #     QMessageBox.information(MainWindow.instance, "通知", success_prompt)

        else:
            with subprocess.Popen(["powershell", "-Command", cmd],stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True) as cmd_progress:
                pass

        return cmd_progress
    except subprocess.TimeoutExpired as e:
        print(Fore.RED + f"{failed_prompt},命令行运行超时: {e}")
    except subprocess.SubprocessError as e:
        print(Fore.RED + f"{failed_prompt},命令行调用错误: {e}")
    except Exception as e:
        print(Fore.RED + f"{failed_prompt},命令行调用未知错误: {e}")
    # finally:
    #     if failed_prompt != '' and MainWindow.instance is not None:
    #         QMessageBox.warning(MainWindow.instance, "警告!", failed_prompt)



def detect_log_finish(log_path, finish_flag, finish_callback):
    # PowerShell 命令，实时监听文件的变化，直到找到目标字符串
    powershell_command = f"Get-Content {log_path} -Wait"
    try:
        # 启动 PowerShell 并监听日志文件
        with subprocess.Popen(["powershell", "-Command", powershell_command],stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, encoding='utf-8',errors='ignore') as process:
            print(f"开始监听 {log_path}，等待目标字符串 '{finish_flag}'...")
            for line in process.stdout:
                print(f'Build日志: {line.strip()}')
                if finish_flag in line:
                    print(f"出现目标字符串 '{finish_flag}'，执行下一步命令...")
                    if finish_callback:
                        finish_callback()
                    break
    except subprocess.TimeoutExpired as e:
        print(Fore.RED + f"运行超时:{e}")
    except Exception as e:
        print(Fore.RED + f"检查日志未知错误: {e}")


def replay(data_filename: str) -> bool:
    temp = soa.reply('play', data_filename)
    print(temp)
    return True
