import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np 
from numpy.fft import fft 
from numpy.fft import fftfreq
import time
import interface
import Serialsetup
import serial
import tkinter as tk

#define variables to use within the circuit

samples=0 #total number of samples taken up to this point

#only windows compatible currently firstly we just want to setup our connection with the arduino over serial
Serialsetup.setup()
arduino=Serialsetup.arduino

lastupdatetime=0

interface.make()


#I dont want to have to call a separate file each time so I've done this instead
N_samples = int(interface.N_frames) 
domain = interface.domain
attenuation = interface.attenuation
coupling = interface.coupling
num_channels = interface.num_channels

for i in range (num_channels):#as specified in the interface if using DC coupling attenuation must be on
    if (coupling[i]=="DC"):
        attenuation[i]="0.25x"

voltages1=np.empty(N_samples) #start with an empty list of voltage values
voltages2=np.empty(N_samples) #start with an empty list of voltage values (maybe make into 2d list later proportional to the number of channels)
timeseries=np.empty(N_samples)
data_to_send=Serialsetup.convertdata(attenuation,coupling,num_channels)
print(data_to_send)
arduino.write(data_to_send)
arduino.reset_input_buffer
arduino.reset_output_buffer#reset buffers
#wait for correct return byte before progressing


print("Number of Samples to take: " + str(N_samples),"\n Domain in use: " + str(domain), "\n Channel Attenuations: " + str(attenuation), "\n Channel Couplings: " + str(coupling))

#this should only be used for the fourier transform, dataperiod may need to be adjusted
#define functions for loop later
#find the syncbite then from there enter a loop of 

def updatedata():
    data1=arduino.read(1).strip()
    if(data1==b'\xab'):#this should be thrown away each time, there is an obvious problem that if a random value equals our checkbyte were a bit cooked
        ch0msb=arduino.read(1).strip()
        ch0lsb=arduino.read(1).strip()
        ch1msb=arduino.read(1).strip()
        ch1lsb=arduino.read(1).strip()
        data2 = arduino.read(1).strip()
        if (data2!=b'\x57'):#if the second checkbyte fails all the data is discarded and we retry, this is approx 1/100 samples
            return updatedata()
        else:
            ch0 = ch0msb + ch0lsb
            ch1 = ch1msb + ch1lsb
            volt0 = int.from_bytes(ch0, byteorder='big', signed= True)*2.5/4096
            volt1 = int.from_bytes(ch1, byteorder='big', signed= True)*2.5/4096
            return volt0, volt1
    else:
        return updatedata()#ie recursive function which calls itself to sync each time.
    

start=time.time()
#Use a while loop to get time passed and when enough time has passed get an update. Currently we dont have continuous time mode. 
if (domain != "cont time"):
    while samples<N_samples:
        results=updatedata()
        voltages1[samples]=results[0]
        voltages2[samples]=results[1]
        now=time.time()
        timeseries[samples]=now-start
        samples+=1



#Plotting section
#define plotting rules (if needed)
#def update_cont_time(frame):#this is for continuous time plotting
fig,ax  = plt.subplots()
x_data, y1_data, y2_data = [], [], []
line1, = ax.plot([], [], lw=2)
line2, = ax.plot([], [], lw=1)
def update(frame):
    global samples
    data=updatedata()
    y1_data.append(data[0])
    y2_data.append(data[1])
    x_data.append(time.time()-start)
    line1.set_data(x_data, y1_data)
    line2.set_data(x_data, y2_data)
    return line1, line2


#produce a list of normalised gaussian values for convolution
lengthgauss=5
if (lengthgauss>N_samples):
    lengthgauss=N_samples
gaussvals=np.zeros(lengthgauss)
gausssum=0
for i in range(lengthgauss):
    gaussvals[i]=1/(2*np.pi) * np.exp(-(i)**2 / (2))#u=0,sigma=1
    gausssum+=gaussvals[i]
gaussvals=gaussvals/gausssum

#define plots
if (domain == 'time'): #for now we will use it that time will be output at the end as opposed to continuous time
    x=timeseries
    y1=np.convolve(voltages1,gaussvals,"same")
    y2=np.convolve(voltages2,gaussvals,"same")
    y1[-lengthgauss:]=voltages1[-lengthgauss:]
    y2[-lengthgauss:]=voltages2[-lengthgauss:]
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.plot(x,y1,label="Channel 1")
    plt.plot(x,y2,label="Channel 2")
    plt.legend()
    plt.show()
    
elif (domain == 'frequency'):
    dataperiod=(timeseries[-1]-timeseries[0])/(N_samples-1)
    fourier1 = fft(voltages1,N_samples)
    fourier2 = fft(voltages2,N_samples)
    freqs = fftfreq(N_samples,dataperiod)
    y1=abs(fourier1)
    y2=abs(fourier2)
    x=freqs
    plt.xlabel("Frequency")
    plt.ylabel("Magnitude")
    plt.scatter(x,y1,label="Channel 1")
    plt.scatter(x,y2,label="Channel 2")
    plt.legend()
    plt.show()

else:#continuous time plotting
    dataperiod=(timeseries[-1]-timeseries[0])/(N_samples-1)
    ax.set_xlim(0,N_samples/5000)
    ax.set_ylim(-3, 3)
    ani = FuncAnimation(fig=fig, func=update, frames=N_samples, fargs=None, interval=40)
    plt.show()


