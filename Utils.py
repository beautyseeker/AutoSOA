import subprocess
import sys
import time
from subprocess import CompletedProcess
from typing import Callable, Union
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
        devices = [line for line in output if "device" in line and not line.startswith("List")]
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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if type(package_name) == str:
            package_name = package_name.decode()
        elif type(package_name) == AppSimplifiedName:
            package_name = package_name.value.decode()
        # 检查包名是否在进程列表中
        if package_name in result.stdout:
            print(f"应用 {package_name} 已启动")
            return True
        else:
            print(f"应用 {package_name} 未启动")
            return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False


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

def run_cmd(cmd: str, success_prompt='', failed_prompt='', block=True):
    try:
        print(f"Executing: {cmd}")
        if block:
            cmd_progress = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if cmd_progress.returncode == 0:
                print(success_prompt)
                print(f"Command Output:\n{cmd_progress.stdout}")
            else:
                print(f'{failed_prompt} Non-zero exit code:\n{cmd_progress.stderr}')

        else:
            with subprocess.Popen(["powershell", "-Command", cmd], bufsize=1,stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, encoding='utf-8',errors='ignore') as cmd_progress:
                pass
                # while True:
                #         line = cmd_progress.stdout.readline().strip()
                #         if line:
                #             print(f"PowerShell Output: {line}")
                #         else:
                #             break

        return cmd_progress
    except subprocess.SubprocessError as e:
        print(Fore.RED + f"exception occur: {e.stderr.decode()}")


def detect_log_finish(log_path, finish_flag, finish_callback):
    # PowerShell 命令，实时监听文件的变化，直到找到目标字符串
    powershell_command = f"Get-Content {log_path} -Wait"

    # 启动 PowerShell 并监听日志文件
    with subprocess.Popen(["powershell", "-Command", powershell_command], bufsize=1,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',errors='ignore') as process:
        print(f"开始监听 {log_path}，等待目标字符串 '{finish_flag}'...")

        print(process.stderr)

        while True:
            # 读取 PowerShell 输出的每一行
            line = process.stdout.readline().strip()
            if line:
                print(f"Build日志: {line}")
                # 检查是否出现目标字符串
                if finish_flag in line:
                    print(f"出现目标字符串 '{finish_flag}'，执行下一步命令...")
                    if finish_callback:
                        finish_callback()
                    # 终止 PowerShell 进程
                    process.terminate()



                    break


def replay(data_filename: str) -> bool:
    temp = soa.reply('play', data_filename)
    print(temp)
    return True
