# main.py
import subprocess
import time
import os

def start_server():
    # Start the server in a separate process
    server_proc = subprocess.Popen(['python', 'server.py'])
    time.sleep(2)  # Give server time to initialize
    return server_proc

def main():
    print("Starting Hybrid Image Protection System...")
    server_proc = start_server()
    try:
        # Run the GUI
        subprocess.run(['python', 'gui_app.py'])
    finally:
        # Clean up
        server_proc.terminate()
        server_proc.wait()
        print("System shut down.")

if __name__ == "__main__":
    main()