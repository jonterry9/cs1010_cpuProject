import psutil
import platform
import time
import os
import signal
import threading as thread
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from itertools import count
from matplotlib import style
from datetime import datetime

svmem = psutil.virtual_memory()

try:
        open('cpu_mem_data.csv', 'r')
except FileNotFoundError:
        df = pd.DataFrame([["CPU","MEM","TIME"]])
        df.to_csv('cpu_mem_data.csv', mode='x', index=False, header=False)
        print('created file')

cpu_data = []
mem_data = []
time_data = []
style.use('fivethirtyeight')
index = count()

def animate(i):
    data = pd.read_csv('cpu_mem_data.csv')
    cpu_data = data.loc[:,'CPU']
    mem_data = data.loc[:,'MEM']
    time_data = data.loc[:,'TIME']
    plt.cla()
    plt.plot(time_data, cpu_data)
    plt.plot(time_data, mem_data)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()



def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_cpu_usage():
        """
        Return total % CPU utilization (avg % usage per core)
        """
        return psutil.cpu_percent()

def get_mem_usage():
        svmem = psutil.virtual_memory()
        return (svmem.used / svmem.total) * 100

def loop_update_data():
        cur_time = 0
        print("thd started")
        while True:
            df = pd.DataFrame([[get_cpu_usage(), get_mem_usage(), cur_time]])
            df.to_csv('cpu_mem_data.csv', mode='a', index=False, header=False)
            time.sleep(1)
            cur_time += 1



print("="*40, "System Information", "="*40)
uname = platform.uname()
print(f"System: {uname.system}")
print(f"Node Name: {uname.node}")
print(f"Release: {uname.release}")
print(f"Version: {uname.version}")
print(f"Machine: {uname.machine}")
print(f"Processor: {uname.processor}")
print("="*40, "CPU Info", "="*40)
# number of cores
print("Physical cores:", psutil.cpu_count(logical=False))
print("Total cores:", psutil.cpu_count(logical=True))
# CPU frequencies
cpufreq = psutil.cpu_freq()
print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
# Memory Information
print("="*40, "Memory Information", "="*40)
# get the memory details
print(f"Total: {get_size(svmem.total)}")

#live graph mem & cpu usage
pid = os.fork()
if(not pid):
        """
        fork() creates a new process (executing program on your computer) called the "child process"
        we say this child process is forked off of the "parent process"
        The child process will begin executing the same code as the parent, starting at the line
        immediatly following fork()
        Here, the child process will run the loop_update_data() function while the parent process
        runs the animation.FuncAnimation() / plt.show() section of the code
        """
        loop_update_data()
else:
        try:
                ani = animation.FuncAnimation(plt.gcf(), animate, 5000)
                plt.tight_layout()
                plt.show()
        finally:
                os.remove('cpu_mem_data.csv')
                with open('cpu_mem_data.csv', 'w') as f:
                        f.write('CPU,MEM,TIME\n')
                os.kill(pid, signal.SIGKILL)  