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
arduino.reset_input_buffer()
arduino.reset_output_buffer()
print(data_to_send.hex())
arduino.write(data_to_send)
print("command recevied: "+str(arduino.read().hex()))
#wait for correct return byte before progressing


print("Number of Samples to take: " + str(N_samples),"\n Domain in use: " + str(domain), "\n Channel Attenuations: " + str(attenuation), "\n Channel Couplings: " + str(coupling))

#this should only be used for the fourier transform, dataperiod may need to be adjusted
#define functions for loop later
#find the syncbite then from there enter a loop of 
rejections=0
def updatedata():
    global rejections
    data1=arduino.read(1).strip()
    if(data1==b'\xab'):#this should be thrown away each time, there is an obvious problem that if a random value equals our checkbyte were a bit cooked
        ch0msb=arduino.read(1).strip()
        ch0lsb=arduino.read(1).strip()
        #data2 = arduino.read(1).strip() remove middle checkbyte
        ch1msb=arduino.read(1).strip()
        ch1lsb=arduino.read(1).strip()
        data3 = arduino.read(1).strip()
        if (data3!=b'\x57'):#if the second or third checkbyte fails all the data is discarded and we retry, this is approx 1/100 samples
            rejections+=1
            return updatedata()
        else:
            ch0 = ch0msb + ch0lsb
            ch1 = ch1msb + ch1lsb
            volt0 = int.from_bytes(ch0, byteorder='big', signed= True)*8/4096
            volt1 = int.from_bytes(ch1, byteorder='big', signed= True)*8/4096
            if (abs(volt0)<7 and abs(volt1)<7):
                return volt0,volt1
            else:
                rejections+=1
                return updatedata()
    else:
        rejections+=1
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
    arduino.reset_input_buffer()#check if this makes the input work
    data=updatedata()
    y1_data.append(data[0])
    y2_data.append(data[1])
    x_data.append(time.time()-start)
    line1.set_data(x_data, y1_data)
    line2.set_data(x_data, y2_data)
    return line1, line2


#produce a list of normalised gaussian values for convolution
# lengthgauss=5
# if (lengthgauss>N_samples):
#     lengthgauss=N_samples
# gaussvals=np.zeros(lengthgauss)
# gausssum=0
# for i in range(lengthgauss):
#     gaussvals[i]=1/(2*np.pi) * np.exp(-(i)**2 / (2))#u=0,sigma=1
#     gausssum+=gaussvals[i]
# gaussvals=gaussvals/gausssum

def lowpass_fft(signal, fs, cutoff):
    N = len(signal)
    # FFT
    spectrum = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, d=1/fs)

    # Keep only frequencies below cutoff
    spectrum[np.abs(freqs) > cutoff] = 0

    # IFFT
    return np.fft.ifft(spectrum).real

#define plots
if (domain == 'time'): #for now we will use it that time will be output at the end as opposed to continuous time
    x=timeseries
    fs=(N_samples-1)/(timeseries[-1]-timeseries[0])
    cutoff=5000#Hz
    y1 = lowpass_fft(voltages1, fs, cutoff)
    y2 = lowpass_fft(voltages2, fs, cutoff)
    for i in range(num_channels):
        if (coupling[0]=="DC"):
            y1*=1.75
        else:
            if (attenuation[0]=="0.25x"):
                y1=y1*2.3
        if (coupling[1]=="DC"):
            y2*=1.75
        else:
            if (attenuation[1]=="0.25x"):
                y2=y2*2.3
    print("averagesampling frequnecy: "+str(fs)+"Hz")#print out useful channel data
    print("Average Value (series 1): "+str(sum(y1)/len(y1)))
    print("Average value (series 2): "+str(sum(y2)/len(y2)))
    print("Max Value (series 1): "+str(max(y1)))
    print("Max Value (series 2): "+str(max(y2)))
    print("Min Value (series 1): "+str(min(y1)))
    print("Min Value (series 2): "+str(min(y2)))
    print("Peak to Peak (series 1): "+str(max(y1)-min(y1)))
    print("Peak to Peak (series 2): "+str(max(y2)-min(y2)))
    # y1square=np.empty(y1)
    # y2square=np.empty(y2)
    # for i in y1square:
    #     i=pow(y1,2)
    # for i in y2square:
    #     i=pow(y2,2)
    # print("RMS value (series 1): "+str(pow((sum(y1square)/len(y1square)),0.5)))
    # print("RMS value (series 2): "+str(pow((sum(y2square)/len(y2square)),0.5)))
    # period=0
    # fourier1=fft(voltages1,N_samples)
    # fourier2=fft(voltages2,N_samples)
    # print("period: "+str(period))
    print(str(rejections)+" samples rejected")
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
    plt.plot(x,y1,label="Channel 1")
    plt.plot(x,y2,label="Channel 2")
    plt.xscale('log')
    plt.legend()
    plt.show()

else:#continuous time plotting
    dataperiod=(timeseries[-1]-timeseries[0])/(N_samples-1)
    ax.set_xlim(0,N_samples/5000)
    ax.set_ylim(-3, 3)
    ani = FuncAnimation(fig=fig, func=update, frames=N_samples, fargs=None, interval=40)
    plt.show()


