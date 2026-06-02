import tkinter as tk
from tkinter import ttk
import numpy as np
from functools import partial

#this code is designed to be easily scalable in terms of number of channels hence uses loops instead of repeating code even though we only use two channels so that by changing num_channels the code could be easily scaled.

num_channels = 2
domain = 'time' #domain always defaults to time
attenuation = ["1x"]*num_channels #store as a tuple of two (number of channels) values
coupling = ["DC"]*num_channels #store as a tuple of two (number of channels) values
N_frames = 0 #domian and number of samples/frames doesnt not need to be sent to the arduino
#labels which will be modified must be declared here as they must be global to all functions
domain_label = 0
attenuation_labels = [0]*num_channels
coupling_labels = [0]*num_channels
Frames_label = 0 
#UI should be initialise outside the function that calls it as it is needed for defining Frames_entry, which is needed in one of the functions so cannot be inside the make() function
UI = tk.Tk()
Frames_entry = tk.Entry(UI)


def switch_domain():
    global domain
    global domain_label
    if (domain == 'time'):
        domain = 'frequency' 
    else:
        domain = 'time'
    domain_label.config(text = "Current Domain: " + domain)

def switch_attenuation(i):
    global attenuation
    global attenuation_labels
    if (attenuation[i] == "1x"):
        attenuation[i] = "0.25x"
    else:
        attenuation[i] = "1x"
    attenuation_labels[i].config(text = "Channel " + str(i+1) + " attenatuion, currently " + attenuation[i])

def switch_coupling(i):
    global coupling
    global coupling_labels
    if (coupling[i] == "DC"):
        coupling[i] = "AC"
    else:
        coupling[i] = "DC"
    coupling_labels[i].config(text = "Channel " + str(i+1) + " coupling, currently " + coupling[i])

#Redundant Function as we are now closing window, if window remains open this becomes useful again
# def change_frames(event):
#     global N_frames
#     global Frames_label
#     global Frames_entry
#     N_frames = Frames_entry.get()
#     Frames_label.config(text = "Change number of samples, currently " + N_frames)


def close_window():
    global N_frames
    N_frames = Frames_entry.get()
    global UI
    UI.destroy()


def make():
    #declare global variables ie ones which will continuously update
    global domain_label
    global attenuation_labels
    global coupling_labels
    global Frames_label
    global N_frames
    global Frames_entry
    global UI
    
    UI.title("Oscilloscope")
    UI.geometry("400x500")
    # add title

    title = tk.Label(UI, text= "Oscilloscope Interface")
    title.pack()

    #add button for switching domain

    domain_label = tk.Label(UI,text = "Current Domain: " + domain)
    domain_label.pack()
    domain_button = tk.Button(UI, text="Switch Domain", font=("Arial", 10),command = switch_domain)
    domain_button.pack(pady=5)

    #add in attenuation buttons
    attenuation_btns = [0]*num_channels
    coupling_btns = [0]*num_channels

    for i in range(num_channels):
        attenuation_labels[i] = tk.Label(UI, text = "Channel " + str(i+1) + " attenatuion, currently 1x", font=("Arial",10) )
        attenuation_labels[i].pack()
        attenuation_btns[i] = tk.Button(UI, text="Change Attenuation", font=("Arial", 10), command = partial(switch_attenuation, i))
        attenuation_btns[i].pack()

    for i in range(num_channels):
        coupling_labels[i] = tk.Label(UI, text = "Channel " + str(i+1) + " coupling, currently DC", font=("Arial",10) )
        coupling_labels[i].pack()
        coupling_btns[i] = tk.Button(UI, text="Change Coupling", font=("Arial", 10), command = partial(switch_coupling, i))
        coupling_btns[i].pack()


    #Use buttons to adjust number of samples as labels was too complicated
    Frames_label = tk.Label(UI, text= "Set number of samples")
    Frames_label.pack()
    Frames_entry.pack()   


    Kill_button = tk.Button(UI, text= "Begin taking samples", command = close_window)
    Kill_button.pack()

    UI.mainloop()


