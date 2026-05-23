import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import numpy as np
#will upodate line below to work on any port later by reading which port the device is attached to
arduino = serial.Serial('COM7', 115200, timeout=1)
t = 0
fig,ax  = plt.subplots()
x_data, y_data = [], []
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, 25)
ax.set_ylim(-1.1, 1.1)

def init():
    line.set_data([], [])
    return line,

def update(frame):
    global t
    x_data.append(t*0.5)
    read = arduino.readline().decode().strip()
    if read:
        y_data.append(read)
    else: 
        y_data.append(0)
    line.set_data(x_data, y_data)
    t+=1
    return line

#frames=np.linspace(0,20,20)
ani = FuncAnimation(fig=fig,func=update,frames=50, interval = 20)
plt.show()
