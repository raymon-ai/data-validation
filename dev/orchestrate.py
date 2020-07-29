import os
import signal
import subprocess
import sys
import time
# Parse command-line arguments.
if len(sys.argv) > 1:
    folder = os.path.abspath(sys.argv[1])
else:
    folder = os.path.abspath(os.getcwd())

# Set up a signal handler so we can stop all Streamlit instances with Ctrl-C.

processes = []


def signal_handler(signal_number, stack_frame):
    for process in processes:
        process.kill()


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if sys.platform == 'win32':
    signal.signal(signal.SIGBREAK, signal_handler)
else:
    signal.signal(signal.SIGQUIT, signal_handler)


# Runs all Python files, but exclude this script to avoid a loop.

this_file = os.path.abspath(__file__)

for basename in os.listdir(folder):
    fname = os.path.join(folder, basename)

    if fname.endswith('.py') and fname != this_file:
        process = subprocess.Popen(['streamlit', 'run', fname])
        processes.append(process)


# Block this script until all processes terminate.

for process in processes:
    process.wait()
    
print("Continuing...")
time.sleep(20)
