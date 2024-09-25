# !/usr/bin/env python
# coding=utf-8
# @Time    : 2022/8/5 16:46
# @Author  : longchao.cai
import json
import time
import zmq
from datetime import datetime


class ZmqClient(object):
    instance = None
    def __init__(self, ip="127.0.0.1", rcv_out=90000, tcp_port=30002, udp_port=30001):
        """
        :param ip:
        :param tcp_port: TCP端口号
        :param udp_port: UDP端口号
        :param rcv_out: TCP接收返回消息超时时间，单位 ms
        """
        self.ip = ip
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.rcv_out = rcv_out
        self.context = zmq.Context()
        self.tcp_socket = None
        self.udp_socket = None
        self.connect()

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(ZmqClient, cls).__new__(cls)
        return cls.instance

    def connect(self):
        if self.tcp_port and self.tcp_socket is None:
            self.tcp_connect()
        if self.udp_port and self.udp_socket is None:
            self.udp_connect()

    def disconnect(self):
        self.tcp_disconnect()
        self.udp_disconnect()

    def tcp_connect(self):
        try:
            self.tcp_socket = self.context.socket(zmq.REQ)
            self.tcp_socket.setsockopt(zmq.LINGER, 0)
            self.tcp_socket.setsockopt(zmq.RCVTIMEO, self.rcv_out)
            self.tcp_socket.connect("tcp://{addr}:{p}".format(addr=self.ip, p=self.tcp_port))
            # self.tcp_socket.bind("tcp://{addr}:{p}".format(addr=self.ip, p=self.tcp_port))
        except Exception as e:
            # print("connect ZMQ-TCP error: {}".format(e))
            self.tcp_socket = None

    def udp_connect(self):
        try:
            self.udp_socket = self.context.socket(zmq.PUB)
            self.udp_socket.connect("tcp://{addr}:{p}".format(addr=self.ip, p=self.udp_port))
        except Exception as e:
            # print("connect ZMQ-UDP error: {}".format(e))
            self.udp_socket = None

    def tcp_disconnect(self):
        try:
            self.tcp_socket.close()
        except Exception:
            pass
            # print("disconnect ZMQ-TCP error: {}".format(e))
        self.tcp_socket = None

    def udp_disconnect(self):
        try:
            self.udp_socket.close()
        except Exception:
            pass
            # print("disconnect ZMQ-UDP error: {}".format(e))
        self.udp_socket = None

    def tcp_send_msg(self, msg_payload, show_log=True):
        recv_msg = {}
        try:
            self.connect()
            if self.tcp_socket is None:
                return recv_msg
            msg_payload = json.dumps(msg_payload).encode('utf-8')
            self.tcp_socket.send(msg_payload)
            if show_log:
                print("{} ZMQ_TCP_REQ:{}".format(datetime.now().strftime('%H:%M:%S.%f')[:-3], msg_payload))
        except Exception as e:
            if show_log:
                print("ZMQ_TCP_REQ error:{}".format(e))
            self.disconnect()

        try:
            recv_msg = json.loads(self.tcp_socket.recv())
            if show_log:
                print("{} ZMQ_TCP_RESP:{}".format(datetime.now().strftime('%H:%M:%S.%f')[:-3], recv_msg))
        except Exception as e:
            if show_log:
                print("ZMQ_TCP_RESP error:{}".format(e))
            self.disconnect()
        finally:
            return recv_msg

    def udp_send_msg(self, msg_payload):
        try:
            # print("UDP接口暂时关闭,请使用TCP接口,nonblocking=False")
            # return
            self.connect()
            if self.udp_socket:
                print("{} ZMQ_UDP_REQ:{}".format(datetime.now().strftime('%H:%M:%S.%f')[:-3], msg_payload))
                msg_payload = json.dumps(msg_payload).encode('utf-8')
                self.udp_socket.send(msg_payload)
        except Exception as e:
            print("ZMQ_UDP_REQ error:{}".format(e))
            self.disconnect()

    # 接口
    def set_auto_response(self, service, data, instance_name="", nonblocking=False):
        """
        data示例:
        1,特定值有关系，其余值固定时，可以一个req对应多个resp子属性
                      request子属性名称              response子属性名称      req和resp的值的关系
        data = {"SetWtiStatusParam.domain": {"ReturnValue.result": {"1": 0,"default": 1}}}
        2,resp的信号值和req有关系时, 支持类代码的字符串逻辑写法,其中req代指收到的req信号的值,
            新写的逻辑建议本地用  eval(xxxx)验证一下返回值是否符合预期
        返回值和req保持一致
        data = {"SetWtiStatusParam.domain": {"ReturnValue.result": "req"}}
        当req大于0时，返回值比req小1，否则为0
        data = {"SetWtiStatusParam.domain": {"ReturnValue.result": "(req - 1) if req > 0 else 0"}}
        3,若docker内有预存逻辑的json文件,可传参绝对路径
        data = "/root/idl/WarningService_et7.json"
        data = "/root/idl/WarningService_et5.json"
        """
        para_dict = {
            "action": "set_auto_response",
            "service": service,
            "instance_name": instance_name,
            "data": data,
        }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def set_config(self, data, nonblocking=False):
        """
        目前支持的格式,主要设置协议信息,格式为后续其他传参准备
        {
            "CbnClmtMgr": {"protocol": "tox"},
            "WarningService": {"protocol": "dds"},
        }
        """
        para_dict = {
            "action": "set_config",
            "data": data,
        }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def start_service(self, service, role="server", instance_name="", nonblocking=False):
        """
        启动模拟服务
        Args:
            service string: 服务名
            instance_name string: 实例名
            role string: 角色 server/client
        """
        para_dict = {
            "action": "start_service",
            "service": service,
            "instance_name": instance_name,
            "role": role
        }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict, show_log=False)

    def stop_service(self, service, instance_name="", nonblocking=False):
        """
        停止模拟服务
        Args:
            service string: 服务名
            instance_name string: 实例名
        """
        para_dict = {
            "action": "stop_service",
            "service": service,
            "instance_name": instance_name,
        }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def send_data(self, service, rpc='', data=None, instance_name="", timeout=5000, nonblocking=False):
        """
        发送数据,不需要区分method/event,不区分发送还是预设返回值
        Args:
            service string: 服务名
            instance_name string: 实例名
            rpc int/string: 可以传rpc id也可以传rpc name，传name时注意和req的message名区分开, 支持未定义的rpc
            data bytes/dict:
                1, 数据字典: key为message.signal.signal结构, 按需发，不需要全部发,例: HvacOnOffReq
                    {
                        "HvacOnOffReq.req_src_type": 1,
                        "HvacOnOffReq.on_off_req": 2,
                        "HvacOnOffReq.frnt_ri_on_off_req": 3,
                        "HvacOnOffReq.sec_le_on_off_req": 1,
                        "HvacOnOffReq.sec_ri_on_off_req": 2,
                        "HvacOnOffReq.thrd_le_on_off_req": 3
                    }
                2, 空字典{}: proto恢复初始值
                3, 直接传十六进制字符串,不经过proto序列化，直接发送， 如 ‘08 00 FF FF’
        Returns:
            dict:proto解析后的数据字典
        """
        self.start_service(service=service, instance_name=instance_name)
        para_dict = {
            "action": "send_data",
            "service": service,
            "instance_name": instance_name,
            "rpc": rpc,
            "data": data,
            "timeout": timeout,
        }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def read_data(self, service, rpc='', instance_name="", timeout=5000):
        """
        读取数据,
            1，rpc支持get_field，且当前模拟的是client,则发送get_field
            2，rpc不支持get_field，则获取当前模拟服务的值
        Args:
            service string: 服务名
            instance_name string: 实例名
            rpc int/string: 可以传rpc id也可以传rpc name，传name时注意和req的message名区分开
        Returns:
            dict:proto解析后的数据字典
        """
        return self.tcp_send_msg({
            "action": "read_data",
            "service": service,
            "instance_name": instance_name,
            "rpc": rpc,
            "timeout": timeout,
        })

    def listen_data(self, service, rpc, sec_time, instance_name=""):
        """
        监听rpc数据, 监听指定rpc的所有收发的内容
        Args:
            service string: 服务名
            instance_name string: 实例名
            rpc int/string: 可以传rpc id也可以传rpc name，传name时注意和req的message名区分开
            sec_time string/int/float: start/stop/时间
        Returns:
            dict:proto解析后的数据字典
        """
        if sec_time in ["start", "stop"]:
            ret = self.tcp_send_msg({
                "action": "listen_data", "service": service, "instance_name": instance_name,
                "rpc": rpc, "listen_cyclic": sec_time
            })
        else:
            self.tcp_send_msg({
                "action": "listen_data", "service": service, "instance_name": instance_name,
                "rpc": rpc, "listen_cyclic": "start"
            })
            time.sleep(sec_time)
            ret = self.tcp_send_msg({
                "action": "listen_data", "service": service, "instance_name": instance_name,
                "rpc": rpc, "listen_cyclic": "stop"
            })
        return ret

    def complex_function(self, switch, data=None):
        """
        一些参数较少的组合功能
        Args:
            switch string:
                1, reload: 重新加载idl数据,
            data int/dict: 部分接口用到的参数
        Returns:
        """
        return self.tcp_send_msg({
            "action": "complex_function",
            "switch": switch,
            "data": data,
        })

    def e2e_error_inject(self, service, instance_name='', rpc=None, switch=True, nonblocking=False):
        """
        注入e2e error
        Args:
            service string: 服务名
            instance_name string: 实例名
            rpc int/string: 可以传rpc id也可以传rpc name，传name时注意和req的message名区分开
            switch bool/dict: 开关
                                True/Flase: 是否注入CRC错误
                                {'counter': 0, 'crc': 0, 'data_id': 0, 'length': 0}: 按具体内容注入偏置量
        Returns:
        e2e_error_inject("VehState", switch=True)
        e2e_error_inject("VehState", switch={'counter': 0, 'crc': 1, 'data_id': 0, 'length': 0})
        """
        if rpc:
            para_dict = {
                "action": "e2e_error_inject",
                "service": service,
                "instance_name": instance_name,
                "rpc": rpc,
                "switch": switch,
            }
        else:
            para_dict = {
                "action": "e2e_error_inject",
                "service": service,
                "instance_name": instance_name,
                "switch": switch,
            }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def pause_event(self, service, instance_name='', rpc=None, switch=True, nonblocking=False):
        """
        暂停周期报文
        Args:
            service string: 服务名
            instance_name string: 实例名
            rpc int/string: 可以传rpc id也可以传rpc name，传name时注意和req的message名区分开
            switch bool: 开关
        Returns:
        """
        if rpc:
            para_dict = {
                "action": "pause_event",
                "service": service,
                "instance_name": instance_name,
                "rpc": rpc,
                "switch": switch,
            }
        else:
            para_dict = {
                "action": "pause_event",
                "service": service,
                "instance_name": instance_name,
                "switch": switch,
            }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def penetrate(self, service, instance_name='', switch=True, nonblocking=False):
        """
        是否透传FIELD数据
        Args:
            service string: 服务名
            instance_name string: 实例名
            switch bool: 开关
        Returns:
        """
        para_dict = {
            "action": "penetrate",
            "service": service,
            "instance_name": instance_name,
            "switch": switch,
        }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def pause_rx_log(self, service, instance_name='', switch=True, nonblocking=False):
        """
        暂停打印接收数据的log
        Args:
            service string: 服务名
            instance_name string: 实例名
            switch bool: 开关
        Returns:
        """
        para_dict = {
            "action": "pause_rx_log",
            "service": service,
            "instance_name": instance_name,
            "switch": switch,
        }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def pause_auto_response(self, service, instance_name='', switch=True, nonblocking=False):
        """
        暂停自动反馈
        Args:
            service string: 服务名
            instance_name string: 实例名
            switch bool: 开关
        Returns:
        """
        para_dict = {
            "action": "pause_auto_response",
            "service": service,
            "instance_name": instance_name,
            "switch": switch,
        }
        if nonblocking:  # 减少网络阻塞
            self.udp_send_msg(para_dict)
        else:
            return self.tcp_send_msg(para_dict)

    def pressure(self, service, instance_name='', switch=True, interval=1000, fixation_interval=False,
                 fixation_payload=False):
        """
        暂停周期报文
        Args:
            service string: 服务名
            instance_name string: 实例名
            switch bool: 开关
            interval int: 发送的间隔时间, ms
            fixation_interval bool: True: 固定interval周期, False: 有定义的按定义
            fixation_payload bool:  True: 固定值, False: 20轮变一次
        Returns:
        """
        para_dict = {
            "action": "pressure",
            "service": service,
            "instance_name": instance_name,
            "switch": switch,
            "interval": interval,
            "fixation_interval": fixation_interval,
            "fixation_payload": fixation_payload,
        }
        return self.tcp_send_msg(para_dict)

    def check_connection(self, service, instance_name=''):
        """
        获取服务连接状态
        Args:
            service string: 服务名
            instance_name string: 实例名
        Returns:
        """
        return self.tcp_send_msg({
            "action": "check_connection",
            "service": service,
            "instance_name": instance_name,
        })

    def check_statistics(self, service, instance_name=''):
        """
        获取服务角色静态信息
        Args:
            service string: 服务名
            instance_name string: 实例名
        Returns:
        """
        return self.tcp_send_msg({
            "action": "check_statistics",
            "service": service,
            "instance_name": instance_name,
        })

    def check_process_statistics(self, ip, port):
        """
        获取服务进程静态信息
        Args:
            service string: 服务名
            instance_name string: 实例名
        Returns:
        """
        return self.tcp_send_msg({
            "action": "check_process_statistics",
            "ip": ip,
            "port": int(port),
        })

    def reply(self, switch, file=''):
        """
        一些参数较少的组合功能
        Args:
            switch string: play/pause/stop
            file string/dict: idl文件夹中的文件名
                            {"excel": "aaa.xlsx", "adhmi_environment": "common-adhmi-adhmi_environment.pb.dat"}
        Returns:
        """
        return self.tcp_send_msg({
            "action": "reply",
            "switch": switch,
            "file": file,
        })

    def get_service_info(self, service):
        """
        检查服务信息
        Args:
            service string: 服务名
            instance_name string: 实例名
        Returns:
        """
        return self.tcp_send_msg({
            "action": "get_service_info",
            "service": service,
        })


def connect_data_paser(connect_data, client_ECU="CDF"):
    ret = False
    s_data = connect_data.get("SERVER_STATUS", dict())
    for c_addr, c_data in connect_data.get("CLIENT_STATUS", dict()).items():
        if client_ECU not in c_addr:
            continue
        c_idl_ver = c_data.get("idl_ver")
        s_addr = c_data.get("server")
        if s_addr:
            print(f"client:[{c_addr}]已连接server:[{s_addr}]")
            ret = True
            s_idl_ver = s_data.get(s_addr, dict()).get("idl_ver")
            print(f"idl_ver:server[{s_idl_ver}] {'==' if s_idl_ver == c_idl_ver else '!='} client[{c_idl_ver}]")
        else:
            print(f"client:[{c_addr}]未连接server, 当前状态:{c_data.get('status')}")
    return ret

