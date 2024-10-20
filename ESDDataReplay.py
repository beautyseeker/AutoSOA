import os
import subprocess
import sys
import time
from colorama import init, Fore
from ZMQClient import ZmqClient
from Utils import is_app_running_ps, wait_until, is_dir_exists_on_device, run_cmd


replay_data_src_path = r"E:\FeiShu\pbdata_play"
replay_cfg_src_path = r"E:\FeiShu\data_adapter_play_debug.json"
replay_cfg_dst_path = "data/user/0/com.nio.metacar/files/AquilaConfig/DA/"
replay_data_dst_path = "data/user/0/com.nio.metacar/files/AquilaData/"
# 定义文件和目标路径的映射
files_to_push = {
    replay_data_src_path: replay_data_dst_path,
    replay_cfg_src_path: replay_cfg_dst_path
}


# 遍历文件字典并执行 adb push 命令
for src_path, dst_path in files_to_push.items():
    if not os.path.exists(src_path):
        print(Fore.RED + f"File dir:{src_path} is not exist")
        break
    if is_dir_exists_on_device(dst_path):
        break
    else:
        run_cmd(f"adb shell mkdir {dst_path}")
    command = f"adb push \"{src_path}\" \"{dst_path}\""
    run_cmd(command)

print(Fore.GREEN + "All replay files Ready.")
run_cmd(f"adb shell stop")
run_cmd(f"adb shell start")

#模拟长按唤出自车界面
long_press = lambda : run_cmd(f"adb shell input swipe 900 700 900 700 2000")
wait_until(is_app_running_ps, package_name="com.nextev.account", delay_wait=20, callback=long_press)

wait_until(is_app_running_ps, package_name="com.nio.metacar")


# 模拟SOA服务发送D挡
soa = ZmqClient()
time.sleep(2)
soa.send_data(service="GearCtrlSrv", instance_name="GearCtrlSrvPri", rpc="IfGearInfo",
              data={'GearInfo.display_act_gear': 3, 'GearInfo.display_act_gear_vld': True})

run_cmd(f"adb shell am broadcast  -a  com.alps.metacar_ACTION_TEST_NAVI_PLUS --ei play_back 1")
