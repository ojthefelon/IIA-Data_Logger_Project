import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np 
from numpy.fft import fft 
from numpy.fft import fftfreq
from serial.tools import list_ports
import time
import interface
import Serialsetup

#define variables to use within the circuit
updateperiod=0.02 #this should be equal to transmission interval on the arduino
voltages=[] #start with an empty list of voltage values
timevals=[] #start with an empty list of time values

t=0 #time variable to be updated each cycle to make calculations shorter, other methods can be used in most cases but will be slower

#only windows compatible currently firstly we just want to setup our connection with the arduino over serial
devices=list_ports.comports()
#need to find out which port is our arduino, we iterate over all devices in our list to see which matchs the description "Arduino Uno". This means if any devices are attached which arent arduino unos we wont use them, creates some obvious issues.
#could modify code below where Arduino intitially starts by sending handshake message over serial till response form PC to allow PC to pick it up
index=0
for i in range(len(devices)):
    if ((devices[i].description)[0:11]=='Arduino Uno'):
        index=i
arduino = serial.Serial(devices[index].device, 115200, timeout=1)
starttime=time.time()
lastupdatetime=0

interface.make()


#I dont want to have to call a separate file each time so I've done this instead
N_samples = int(interface.N_frames) 
domain = interface.domain
attenuation = interface.attenuation
coupling = interface.coupling

print("Number of Samples to take: " + str(N_samples),"\n Domain in use: " + str(domain), "\n Channel Attenuations: " + str(attenuation), "\n Channel Couplings: " + str(coupling))

#Write parameters for attenuation and coupling over serial to the arduino



#define functions for loop later
#store all the voltage data so that mathematical manipulations. i.e. Fourier transforms can be performed
def updatedata():
    voltages.append(float(arduino.readline().decode().strip()))
    timevals.append(t*updateperiod)

#Use a while loop to get time passed and when enough time has passed get an update. Currently we dont have continuous time mode. 
while t<N_samples:
    now = time.time()
    timepassed=now-lastupdatetime #everything is kept on the same time keeping as everything only needs to be updated when a new sample comes in
    if (timepassed>updateperiod):
        lastupdatetime=now
        updatedata()
        t+=1

#continuous time not implemented yet as this requires an entire restructuring of the code and would result in two different streams, can be done later after communication is dealt with

if (domain == 'time'):
    x=timevals
    y=voltages

elif (domain == 'frequency'):
    fourier = fft(voltages,N_samples)
    freqs = fftfreq(N_samples,updateperiod)
    y=abs(fourier)
    x=freqs


#plot the graph
plt.scatter(x,y)
plt.show()
