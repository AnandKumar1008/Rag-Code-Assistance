import paramiko
import time
import requests
import sys

HOSTNAME = "192.168.51.69"
USERNAME = "anandkumar"
PASSWORD = "anand123"
REMOTE_DIR = "/data1/anandkumar/rag_assistant"

print("Connecting via SSH to sync and test...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=10)

# Sync backend files
import subprocess
print("Syncing files using deploy script...")
subprocess.run(["python", "deploy.py"], cwd=r"d:\Anti_gravity\rag_assistant")

print("\nStarting Uvicorn server in the background...")
# Start server and pipe output to a log file
start_cmd = f"cd {REMOTE_DIR} && source venv/bin/activate && nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 & echo $!"
stdin, stdout, stderr = client.exec_command(start_cmd)
pid = stdout.read().decode('utf-8').strip()
print(f"Server started with PID: {pid}")

print("Waiting 10 seconds for server to boot...")
time.sleep(10)

print("Sending test request to http://192.168.51.69:8000/chat...")
try:
    response = requests.post("http://192.168.51.69:8000/chat", json={"query": "Hello, how does LangGraph work?"}, timeout=30)
    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json())
except Exception as e:
    print("Failed to reach server:", e)
    # Fetch logs to see why it failed
    print("Fetching server logs...")
    _, stdout_log, _ = client.exec_command(f"cat {REMOTE_DIR}/server.log")
    print(stdout_log.read().decode('utf-8'))

print("Killing the test server...")
client.exec_command(f"kill {pid}")
client.close()
print("E2E Test completed.")
