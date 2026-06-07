import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np 
from numpy.fft import fft 
from numpy.fft import fftfreq
import time
import interface
import Serialsetup
import serial

#define variables to use within the circuit
dataperiod=1/200000#change this according to sample frequency, this is used for axes and FFT frequencies so will affect those.
voltages1=[] #start with an empty list of voltage values
voltages2=[] #start with an empty list of voltage values (maybe make into 2d list later proportional to the number of channels)

samples=0 #total number of samples taken up to this point

#only windows compatible currently firstly we just want to setup our connection with the arduino over serial
Serialsetup.setup()
arduino=Serialsetup.arduino

starttime=time.time()
lastupdatetime=0

interface.make()


#I dont want to have to call a separate file each time so I've done this instead
N_samples = int(interface.N_frames) 
domain = interface.domain
attenuation = interface.attenuation
coupling = interface.coupling
num_channels = interface.num_channels

data_to_send=Serialsetup.convertdata(attenuation,coupling,num_channels)
print(data_to_send)
arduino.write(data_to_send)
#add the above back later when the PC needs to configure the arduino

print("Number of Samples to take: " + str(N_samples),"\n Domain in use: " + str(domain), "\n Channel Attenuations: " + str(attenuation), "\n Channel Couplings: " + str(coupling))

timevals=np.linspace(0,(N_samples-1)*dataperiod,N_samples) #create an array for timevals to be plotted (if needed) where we assume that each value is sampled once each data period

#define functions for loop later
#find the syncbite then from there enter a loop of 

synced = False
def syncdata():
    global synced
    global arduino
    data=arduino.read(5).strip()
    if (data[0]==171):
        synced = True
        return
    else:
        arduino.read(1).strip()#throaway one byte to wrap around
        syncdata()#keep calling itself till it loops back around and finds the sync bite

def updatedata():
    global synced
    if not synced:
        syncdata()
    syncbyte=arduino.read().strip()#this should be thrown away each time
    ch0msb=arduino.read().strip()
    ch0lsb=arduino.read().strip()
    ch1msb=arduino.read().strip()
    ch1lsb=arduino.read().strip()
    ch0 = ch0msb + ch0lsb
    ch1 = ch1msb + ch1lsb
    volt0 = int.from_bytes(ch0, byteorder='big', signed= True)
    volt1 = int.from_bytes(ch1, byteorder='big', signed= True)
    return volt0,volt1
    


#Use a while loop to get time passed and when enough time has passed get an update. Currently we dont have continuous time mode. 
while samples<N_samples:
    results=updatedata()
    voltages1.append(results[0])
    voltages2.append(results[1])
    samples+=1

#continuous time not implemented yet as this requires an entire restructuring of the code and would result in two different streams, can be done later after communication is dealt with

if (domain == 'time'): #for now we will use it that time will be output at the end as opposed to continuous time
    x=timevals
    y1=voltages1
    y2=voltages2
    plt.plot(x,y1)
    plt.plot(x,y2)
    plt.show()
    

if (domain == 'frequency'):
    fourier1 = fft(voltages1,N_samples)
    fourier2 = fft(voltages2,N_samples)
    freqs = fftfreq(N_samples,dataperiod)
    y1=abs(fourier1)
    y2=abs(fourier2)
    x=freqs
    plt.scatter(x,y1)
    plt.scatter(x,y2)
    plt.show()



