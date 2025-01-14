import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
import pyttsx3
import os

# Initialize the main window
root = tk.Tk()
root.title("Text to Speech")
root.geometry("900x450+200+200")
root.resizable(False, False)
root.configure(bg="#305065")

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

def speaknow():
    text = text_area.get(1.0, END).strip()  # Get text from the text area
    gender = gender_combobox.get()  # Get selected gender
    speed = speed_combobox.get()  # Get selected speed
    voices = engine.getProperty('voices')  # Get available voices

    # Set voice based on gender
    if gender == 'Male':
        engine.setProperty('voice', voices[0].id)  # Male voice
    else:
        engine.setProperty('voice', voices[1].id)  # Female voice

    # Set speed
    if speed == 'Fast':
        engine.setProperty('rate', 250)  # Fast speed
    elif speed == 'Slow':
        engine.setProperty('rate', 100)  # Slow speed
    else:
        engine.setProperty('rate', 150)  # Normal speed

    # Speak text if not empty
    if text:
        engine.say(text)
        engine.runAndWait()

def download():
    text = text_area.get(1.0, END).strip()  # Get text from the text area
    if not text:
        # Display a message if no text is entered
        messagebox.showwarning("No Text", "Please enter some text to save.")
        return

    # Ask user where to save the file
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(text)

# Set icon
image_icon = PhotoImage(file="speak.png")  # Ensure the file exists
root.iconphoto(False, image_icon)

# Top Frame
Top_frame = Frame(root, bg="white", width=900, height=100)
Top_frame.place(x=0, y=0)

# Text Label
Label(Top_frame, text="TEXT TO SPEECH", font="arial 20 bold", bg="white", fg="black").place(x=120, y=30)

# Logo
Logo = PhotoImage(file="speaker logo.png")  # Ensure the file exists
Label(Top_frame, image=Logo, bg="white").place(x=10, y=5)

# Text Area
text_area = Text(root, font="Roboto 20", bg="white", relief=GROOVE, wrap=WORD)
text_area.place(x=10, y=150, width=500, height=250)

# Labels for Gender and Speed
Label(root, text="VOICE", font="arial 15 bold", bg="#305065", fg="white").place(x=580, y=160)
Label(root, text="SPEED", font="arial 15 bold", bg="#305065", fg="white").place(x=760, y=160)

# Gender Combobox
gender_combobox = Combobox(root, values=['Male', 'Female'], font="arial 14", state='readonly', width=10)
gender_combobox.place(x=550, y=200)
gender_combobox.set('Male')

# Speed Combobox
speed_combobox = Combobox(root, values=['Fast', 'Normal', 'Slow'], font="arial 14", state='readonly', width=10)
speed_combobox.place(x=730, y=200)
speed_combobox.set('Normal')

# Speak Button
imageicon = PhotoImage(file="speak.png")  # Ensure the file exists
btn = Button(root, text="Speak", compound=LEFT, image=imageicon, width=130, font="arial 14 bold", command=speaknow)
btn.place(x=550, y=280)

# Save Button
imageicon2 = PhotoImage(file="download.png")  # Ensure the file exists
save = Button(root, text="Save", compound=LEFT, image=imageicon2, width=130, bg="#39c790", font="arial 14 bold", command=download)
save.place(x=730, y=280)

# Run the Tkinter event loop
root.mainloop()
