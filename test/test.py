import sys
import os
import subprocess
import ctypes

def get_admin(*_):
    # Check if running with admin privileges
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    # Relaunch the script with admin privileges if needed
    def run_as_admin():
        if not is_admin():
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([str(arg) for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

    # Run the script with admin permissions
    run_as_admin()

get_admin()

command = 'C:\\Windows\\System32\\netsh.exe advfirewall set allprofiles state off'
res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("out", res.stdout)
print("err", res.stderr)
