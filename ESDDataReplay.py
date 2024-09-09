import os
import subprocess
import sys
import time
from colorama import init, Fore
from ZMQClient import ZmqClient
from Utils import is_app_running_ps, wait_until

replay_data_src_path = r"/home/nio/Desktop/pbdata_play"
replay_cfg_src_path = r"/home/nio/Desktop/data_adapter_play_debug.json"
replay_cfg_dst_path = "data/user/0/com.nio.metacar/files/AquilaConfig/DA/"
replay_data_dst_path = "data/user/0/com.nio.metacar/files/AquilaData/"
# 定义文件和目标路径的映射
files_to_push = {
    replay_data_src_path: replay_data_dst_path,
    replay_cfg_src_path: replay_data_dst_path
}


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


# 遍历文件字典并执行 adb push 命令
for src_path, dst_path in files_to_push.items():
    if not os.path.exists(src_path):
        print(Fore.RED + f"File dir:{src_path} is not exist")
        break
    if not os.path.exists(dst_path):
        run_cmd(f"adb shell mkdir {dst_path}")
    command = f"adb push \"{src_path}\" \"{dst_path}\""
    if run_cmd(command):
        sys.exit(-1)

print(Fore.GREEN + "All replay files have been pushed.")
run_cmd(f"adb shell stop")
run_cmd(f"adb shell start")
wait_until(is_app_running_ps(package_name="com.nio.metacar"))
# 模拟SOA服务发送D挡
soa = ZmqClient()
time.sleep(2)
soa.send_data(service="GearCtrlSrv", instance_name="GearCtrlSrvPri", rpc="IfGearInfo",
              data={'GearInfo.display_act_gear': 3, 'GearInfo.display_act_gear_vld': True})

run_cmd(f"adb shell am broadcast  -a  com.alps.metacar_ACTION_TEST_NAVI_PLUS --ei play_back 1")
