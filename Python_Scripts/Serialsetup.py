import serial
from serial.tools import list_ports
import math

arduino = serial.Serial()
list_ports


def setup():
    global arduino
    devices=list_ports.comports()
    #need to find out which port is our arduino, we iterate over all devices in our list to see which matchs the description "Arduino Uno". This means if any devices are attached which arent arduino unos we wont use them, creates some obvious issues.
    #could modify code below where Arduino intitially starts by sending handshake message over serial till response form PC to allow PC to pick it up
    index=0
    for i in range(len(devices)):
        if ((devices[i].description)[0:11]=='Arduino Uno'):
            index=i
    arduino = serial.Serial(devices[index].device, 1000000, stopbits=1)

def convertdata(att,cpl,num_ch): 
    numbits=num_ch*2   #calculate the number of bits we'll need to send, though the arduino code would need to be modified if this number isnt 8
    maxbits=numbits
    if (numbits%8!=0): #as theres only 3 cases well just use nested if statements
        if (numbits%4==0):
            numbits+=4
        elif ((numbits-2)%8==0):
            numbits+=6
        else:
            numbits+=2
    num=[0]*numbits #create a list into which each parameter will be placed. the order of this will be channelwise ie index0=ch0attenuation index1=ch0coupling index2=ch1attenuation etc
    numbytes=int(numbits//8) #convert from a number of bits to a number of bytes
    for i in range (maxbits):
        if (i & 1) == 0:
            if (att[i//2]=="1x"):
                num[i]=1
            else:
                num[i]=0
        else:
            if (cpl[(i-1)//2]=="DC"):
                num[i]=1
            else:
                num[i]=0
    number=0
    for i in range(maxbits):
        number+=num[i]*pow(2,i)
    sendbyte=number.to_bytes(numbytes,'little',signed = False)
    return sendbyte

def makecheckbyte(num_ch):#function now redundant due to changes in the arduino code.
    numbytestosend=math.ceil(num_ch/4)
    sendbyte=numbytestosend.to_bytes(1,'little',signed = False)
    return sendbyte
