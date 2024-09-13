import os
import subprocess
import sys
import time
from colorama import init, Fore
from ZMQClient import ZmqClient
from Utils import *


replay_data_src_path = r"/home/nio/Desktop/pbdata_play"


#模拟长按唤出自车界面
if is_app_running_ps(AppSimplifiedName.ESD.value):
    if set_gear(GearStatus.R):
        # 将SAPA_STS切换为IN_SEARCH
        ZmqClient.instance.send_data(service='PrkgFuncMgr', rpc='PrkgStsInfo', data={'PrkgStsInfoData.sapa_sts': 1})
        # 调用数据回放
        ZmqClient.instance.reply(switch='play',
                                 file='0227a2c0-6d7d-4dde-acca-ab67296d3950_common-vehicle_out-sapa_ui_results_eth_1724224546786993599.pb.dat')
    else:
        print(f"Switch Gear Failed!")
        sys.exit(-1)

while is_app_running_ps(AppSimplifiedName.ESD.value) is False:
    if is_app_running_ps(AppSimplifiedName.SIG_PAGE):
        long_press = lambda: run_cmd(f"adb shell input swipe 900 700 900 700 2000")
        wait_until(is_app_running_ps, package_name=b"com.nio.metacar", callback=long_press)
        wait_until(is_app_running_ps, package_name=AppSimplifiedName.ESD.value)
    else:
        wait_until(is_app_running_ps, package_name=AppSimplifiedName.SIG_PAGE.value)



