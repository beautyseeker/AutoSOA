import subprocess
import sys
import time
from typing import Callable, Union
from colorama import init, Fore
from enum  import IntEnum, Enum

from ZMQClient import ZmqClient


class GearStatus(IntEnum):
    P = 0,
    R = 1,
    N = 2,
    D = 3,
    Invalid = -1000

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


def wait_until(condition: Callable[..., bool], *args,  interval=2, timeout=150, delay_wait=0, callback=None,**kwargs,):
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

def run_cmd(cmd: str) -> bool:
    try:
        print(f"Executing: {cmd}")
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Command Output:\n{result.stdout.decode()}")
        if result.returncode == 0:
            return True
        return False
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"An error occurred while pushing: {e.stderr.decode()}")
        return False


def get_cur_gear() -> GearStatus:
    soa = ZmqClient()
    data_dict = soa.read_data("GearCtrlSrv", "IfGearInfo", instance_name="GearCtrlSrvPri")
    try:
        gear = GearStatus(data_dict['data']['GearInfo']['display_act_gear'])
    except ValueError:
        gear = GearStatus.Invalid
    return gear

def set_gear(gear: Union[int, GearStatus]) -> bool:
    soa = ZmqClient()
    soa.send_data(service="GearCtrlSrv", instance_name="GearCtrlSrvPri", rpc="IfGearInfo",
              data={'GearInfo.display_act_gear': gear, 'GearInfo.display_act_gear_vld': True})
    cur_gear = get_cur_gear()
    return gear == cur_gear

def replay(data_filename: str) -> bool:
    soa = ZmqClient()
    temp = soa.reply('play', data_filename)
    print(temp)
    return True
