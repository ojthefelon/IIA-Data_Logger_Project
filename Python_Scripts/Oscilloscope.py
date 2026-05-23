import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import numpy as np 
from serial.tools import list_ports
import time
import tkinter as tk
#define variables to use within the circuit
updateperiod=0.02 #this should be equal to transmission interval on the arduino
voltages=[] #start with an empty list of voltage values
timevals=[] #start with an empty list of time values
domain='time' #define default domain as time domain
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

#create UI using TKinter
UI=tk.Tk()
UI.title("Oscilloscope")
UI.geometry("400x500")
add_button = tk.Button(UI, text="Switch Domain", width=20, font=("Arial", 10))
add_button.pack(pady=5)
UI.mainloop()

#define functions for loop later
def updatedata():
    voltages.append(arduino.readline().decode().strip())
    timevals.append(t*updateperiod)


#Use a while loop to get time passed and when enough time has passed get an update.
while True:
    now = time.time()
    timepassed=now-lastupdatetime #everything is kept on the same time keeping as everything only needs to be updated when a new sample comes in
    if (timepassed>updateperiod):
        lastupdatetime=now
        updatedata()
        t=+1

