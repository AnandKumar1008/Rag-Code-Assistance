import paramiko
import os
import sys

HOSTNAME = "192.168.51.69"
USERNAME = "anandkumar"
PASSWORD = "anand123"
LOCAL_DIR = r"d:\Anti_gravity\rag_assistant"
REMOTE_DIR = "/data1/anandkumar/rag_assistant"

def sync_directory(sftp, local_dir, remote_dir):
    print(f"Ensuring remote directory exists: {remote_dir}")
    try:
        sftp.stat(remote_dir)
    except IOError:
        print(f"Creating remote directory: {remote_dir}")
        sftp.mkdir(remote_dir)

    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"

        # Skip the deploy script and virtual environments
        if item in ['deploy.py', 'node_modules', '.git', '__pycache__', '.venv', 'venv']:
            continue

        if os.path.isfile(local_path):
            print(f"Syncing {local_path} -> {remote_path}")
            sftp.put(local_path, remote_path)
        elif os.path.isdir(local_path):
            sync_directory(sftp, local_path, remote_path)

def main():
    print("Connecting to server...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=10)
        
        sftp = client.open_sftp()
        print(f"Syncing local {LOCAL_DIR} to remote {REMOTE_DIR}...")
        sync_directory(sftp, LOCAL_DIR, REMOTE_DIR)
        sftp.close()
        
        print("Executing setup script on remote server...")
        # Make sure remote dir has setup.sh executable and run it
        setup_cmd = f"cd {REMOTE_DIR} && chmod +x setup.sh && ./setup.sh"
        stdin, stdout, stderr = client.exec_command(setup_cmd)
        
        # Read streaming output
        for line in iter(stdout.readline, ""):
            print(line, end="")
            
        err = stderr.read().decode('utf-8')
        if err:
            print(f"Errors:\n{err}")

        client.close()
        print("Deployment complete.")
    except Exception as e:
        print(f"Error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
