import socket
import threading
import zmq

from ZMQClient import ZmqClient

soa = ZmqClient()


soa.send_data("GearCtrlSrv", "IfGearInfo", instance_name="GearCtrlSrvPri",
                          data={"GearInfo.display_act_gear": 1, "GearInfo.display_act_gear_vld": 1}, )

print("Finish")
# while True:
#     received_data = soa.tcp_socket.recv_string()  # 接收数据并解码为字符串
#     if not received_data:
#         break
#     print("收到Unity信息:", received_data)


# 外部开闭信号



# 外部灯光信号
