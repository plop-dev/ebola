import subprocess
import os
import sys
import ctypes

# Default working directory
working_dir = "."

# File where the results will be saved
output_file_path = "cmd_output.txt"

# Create or clear the output file
with open(output_file_path, 'w') as f:
    pass

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

# Function to execute a command and save its output
def doCMD(cmd, working_dir, output_file_path):
    # Check if command is 'cd'
    if cmd.startswith("cd "):
        vals = cmd.split(" ")
        if vals[1].startswith("/"):
            working_dir = vals[1]
        else:
            working_dir = os.path.join(working_dir, vals[1])
        
        # Change the working directory
        os.chdir(working_dir)
        
        with open(output_file_path, 'a') as f:
            f.write(f"\n$ {cmd}\n")
    else:
        # Execute the command and get the output
        result = subprocess.check_output(cmd, shell=True, cwd=working_dir)
        with open(output_file_path, 'a') as f:
            f.write(f"\n$ {cmd}\n")
            f.write(result.decode("utf-8") + "\n")
    
    return working_dir

# Main loop to read commands and execute them
def command_loop(working_dir, output_file_path):
    while True:
        cmd = input("Enter command (or type 'exit' to quit): ")
        if cmd.lower() == "exit":
            break
        working_dir = doCMD(cmd, working_dir, output_file_path)

# Run the command loop
command_loop(working_dir, output_file_path)
