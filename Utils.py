import subprocess
import sys
import time


def is_app_running_ps(package_name):
    try:
        # 使用 adb shell ps 命令列出进程
        result = subprocess.run(
            ["adb", "shell", "ps"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

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


def wait_until(condition, *args,  interval=2, timeout=150, **kwargs,):
    start = time.time()
    while not condition(*args, **kwargs) and time.time() - start < timeout:
        time.sleep(interval)
    if time.time() - start > timeout:
        print("TimeOut!")
        sys.exit(-1)
    print("condition met!")
