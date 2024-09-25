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

conor_area_signals = ["车门", "车窗", "把手"]
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
    data_dict = soa.read_data("GearCtrlSrv", "IfGearInfo", instance_name="GearCtrlSrvPri")
    try:
        gear = GearStatus(data_dict['data']['GearInfo']['display_act_gear'])
    except ValueError:
        gear = GearStatus.Invalid
    return gear

def set_gear(gear: Union[int, GearStatus]) -> bool:
    soa.send_data(service="GearCtrlSrv", instance_name="GearCtrlSrvPri", rpc="IfGearInfo",
              data={'GearInfo.display_act_gear': gear, 'GearInfo.display_act_gear_vld': True})
    cur_gear = get_cur_gear()
    return gear == cur_gear

def replay(data_filename: str) -> bool:
    temp = soa.reply('play', data_filename)
    print(temp)
    return True

def set_door_stat(area: int, stat: int) -> bool:
    """
    :param area: 从左上角开始area为0,俯视顺时针方向递增
    :param stat: 2:开门, 1:关门
    :return:本次状态设置是否成功
    """
    soa.send_data(service="DoorOpenMgr", rpc="DoorOpenSts",
                  data={f"DoorOpenStatus.door_sts[{area}].door_ajar_sts_validity": 1,
                        f"DoorOpenStatus.door_sts[{area}].door_ajar_sts": stat})

def get_door_stat() -> list:
    data_dict = soa.read_data(service="DoorOpenMgr", rpc="DoorOpenSts")
    try:
        door_stat_list = [item.get('door_ajar_sts', -1) for item in
                          data_dict['data']['DoorOpenStatus']['door_sts']]
        return door_stat_list
    except ValueError or IndexError:
        return []


def set_door_handle_stat(area: int, stat: int) -> bool:
    """
    :param area: 从左上角开始area为0,俯视顺时针方向递增
    :param stat: 2:收起, 1:展开
    :return:
    """
    soa.send_data(service="DoorHndlMgr", rpc="DoorHndlSts",
                  data={f"DoorHndlStatus.side_door_hndl_sts[{area}].door_hndl_sts": stat})


def get_door_handle_stat() -> list:
    """
    输入为{'soakey': }组成的字典列表

    :return:将字典列表转换为整型列表，转换规则为输出字典条目下的door_hdnl_sts值,若不存在则输出-1
    """
    data_dict = soa.read_data(service="DoorHndlMgr", rpc="DoorHndlSts")
    try:
        door_stat_list = [item.get('door_hndl_sts', -1) for item in data_dict['data']['DoorHndlStatus']['side_door_hndl_sts']]
        return door_stat_list
    except ValueError or IndexError:
        return []

def get_window_stat() -> list:
    """
    输入为{'soakey': }组成的字典列表

    :return:将字典列表转换为整型列表，转换规则为输出字典条目下的win_open_value值,若不存在则输出-1
    """
    data_dict = soa.read_data(service="WinMgr", rpc="WinSts")
    try:
        door_stat_list = [item.get('win_open_value', -1) for item in data_dict['data']['WinStsInfo']['win_status_info']]
        return door_stat_list
    except ValueError or IndexError:
        return []


def set_window_stat(area: int, stat: int) -> bool:
    """
    :param area: 从左上角开始area为0,俯视顺时针方向递增
    :param stat: 2:开门, 1:关门
    :return:本次状态设置是否成功
    """
    if stat == 1:
        open_value = 100
    else:
        open_value = 0
    soa.send_data(service="WinMgr", rpc="WinSts",
                  data={f"WinStsInfo.win_status_info[{area}].win_open_value": open_value})

def set_hood_stat(stat: int)-> bool:
    """设置前盖开闭状态"""
    soa.send_data(service="HoodMgr", rpc="CentHoodSts",
                  data={"HoodStatus.hood_ajar_sts": stat})


def get_hood_stat() -> int:
    data_dict = soa.read_data(service="HoodMgr", rpc="CentHoodSts")
    data_item = data_dict['data']['HoodStatus']
    return data_item.get('hood_ajar_sts', -1)

def set_trunk_lid_stat(stat: int) -> bool:
    open_value = 100 if stat == 2 else 0
    soa.send_data(service="PlgMgr", rpc="CentPlgSts",
                  data={"PlgStatus.tr_ajar_sts": stat, "PlgStatus.plg_posn": open_value})

def get_trunk_lid_stat() -> int:
    data_dict = soa.read_data(service="PlgMgr", rpc="CentPlgSts")
    data_item = data_dict['data']['PlgStatus']
    return data_item.get('PlgStatus.tr_ajar_sts', -1)

def set_charger_stat(stat: int) -> bool:
    """
    设置充电盖开闭状态
    :param stat: 2开启 1关闭
    :return:
    """
    soa.send_data(service="ChrgrGateMgr", rpc="ChrgrGateWorkSts",
                  data={"ChrgrGateWorkStatus.chrgr_port_ajar_sts": stat})

def get_charger_stat() -> int:
    data_dict = soa.read_data(service="ChrgrGateMgr", rpc="ChrgrGateWorkSts")
    data_item = data_dict['data']['ChrgrGateWorkStatus']
    return data_item.get('chrgr_port_ajar_sts', -1)

def set_mirror_stat(stat: int) -> int:
    soa.send_data(service="MirrFoldMgr", rpc="MirrFoldSts",
                  data={f"MirrFoldStsInfo.left_mirr_fold_sts": stat})

def get_mirror_stat() -> list:

    data_dict = soa.read_data(service="MirrFoldMgr", rpc="MirrFoldSts")
    try:
        door_stat_list = [item.get('left_mirr_fold_sts', -1) for item in data_dict['data']['MirrFoldStsInfo']]
        return door_stat_list
    except ValueError or IndexError:
        return []


def get_conor_signal_group(area: int) -> dict:
    conor_signal_group = [get_door_stat()[area], get_window_stat()[area], get_door_handle_stat()[area]]
    return dict(zip(conor_area_signals, conor_signal_group))
