import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import numpy as np
#will upodate line below to work on any port later by reading which port the device is attached to
# arduino = serial.Serial('COM7', 115200, timeout=1)
# t = 0
# fig,ax  = plt.subplots()
# x_data, y_data = [], []
# line, = ax.plot([], [], lw=2)
# ax.set_xlim(0, 25)
# ax.set_ylim(-1.1, 1.1)
# command = 0 
# attenuation_coupling = (False,False,False,False) #length corresponds to double number of channels, index 0,1 correspond to attenuation Control, 2 and 3 to coupling control
# command = 0

# def definecommand(): #we will use a 1 byte variable to communicate commands to the arduino, the only things that need communicated are attenuation and coupling so 32 total possible states, 2 bits needed to define state for each channel.
#     global attenuation_coupling
#     global command
#     command<<1 
#     for i in attenuation_coupling:
#         if attenuation_coupling[-(i+1)]:
#             command+=1   
    

# def init():
#     line.set_data([], [])
#     return line,

# def update(frame):
#     global t
#     x_data.append(t*0.5)
#     read = arduino.readline().decode().strip()
#     if read:
#         y_data.append(read)
#     else: 
#         y_data.append(0)
#     line.set_data(x_data, y_data)
#     arduino.write(definecommand)
#     print(arduino.readline())
#     t+=1
#     return line

# #frames=np.linspace(0,20,20)
# ani = FuncAnimation(fig=fig,func=update,frames=50, interval = 20)
# plt.show()

def gaussian(x, sigma):#this will be used later for smoothing
    return 1/(2*np.pi) * np.exp(-(x)**2 / (2 * sigma**2))

length=5
sd = 2
sum=0
convolutions = [0]*length
for i in range(len(convolutions)): #need to normalise this
    convolutions[i]=gaussian(i,sd)
    sum+=convolutions[i]
convolutions=convolutions/sum
print(convolutions)
