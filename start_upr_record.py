import threading
import time

import requests
import json
from datetime import datetime
import subprocess
import os.path

from Utils import run_cmd


def stop_upr_recording():
    time.sleep(30)
    run_cmd(r"E:\\Tools\\UnityUPR\\UPRDesktop.exe --stop")

stop_thread = threading.Thread(target=stop_upr_recording)


api_endpoint = "http://10.132.134.40/open-api/sessions"
auth_header = "Basic dWR4RHMwZnFpN0poT0ljbU9qUnFMb2haWkdSUnd0a1g6VFpjcjNIR1RCUFZBdXZPTHRudDlUbTN6ajkyZ0xiTWU="

# Generate current timestamp in the format YYYYMMDDHHMM
timestamp = datetime.now().strftime("%Y%m%d%H%M")

# Create the session name with the timestamp
session_name = f"metacar-{timestamp}"

session_request = {
    "AbnormalFrameTimeThreshold": 60,
    "CaptureWebGL": False,
    "EnableADBMemoryCollection": False,
    "EnableAbnormalFrame": False,
    "EnableAutoObjectSnapshot": True,
    "EnableCaptureRenderingThread": True,
    "EnableDeepLua": False,
    "EnableDeepMono": True,
    "EnableOverdrawMonitor": True,
    "EnableOverdrawScreenshot": True,
    "FrameLockEnabled": False,
    "FrameLockFrequency": 30,
    "GCCallStackEnabled": True,
    "GPUProfileEnabled": True,
    "GPUProfileFrequency": 1000,
    "GameName": "metacar",
    "GameVersion": "1",
    "Monitor": False,
    "ObjectSnapshotFrequency": 5,
    "PackageName": "com.nio.metacar",
    "ProjectId": "17b6c10b-389a-4fb5-9158-3a4eb9b3f187",
    "ScreenshotEnabled": True,
    "ScreenshotFrequency": 4,
    "SessionName": session_name,
    "ShareReport": True,
    "Tags": ["string"],
    "UnityVersion": "2022.2"
}

# Send POST request
headers = {
    "accept": "application/json",
    "authorization": auth_header,
    "Content-Type": "application/json"
}

response = requests.post(api_endpoint, headers=headers, data=json.dumps(session_request))

# Print full response
print("Full response:", response.text)

# Extract and print SessionId
try:
    response_json = response.json()
    session_id = response_json.get("SessionId", "SessionId not found")
    print("SessionId:", session_id)
except json.JSONDecodeError:
    print("Failed to decode JSON response")

# If session_id is found, execute the next command
if session_id and session_id != "SessionId not found":
    # Construct the command
    command = [
        r'E:\\Tools\\UnityUPR\\UPRDesktop.exe',
        "-p", "127.0.0.1",  # Replace <device_ip> with the actual device IP
        "-s", session_id,
        "-n", "com.nio.metacar"  # Replace with the actual package name if different
    ]

    # Change directory and run the command
    try:
        stop_thread.start()
        res = subprocess.run(command, check=True)
        print(res.stdout.decode())
        print("UPRDesktop.exe executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing UPRDesktop.exe: {e}")
else:
    print("No valid SessionId found. UPRDesktop.exe will not be executed.")
