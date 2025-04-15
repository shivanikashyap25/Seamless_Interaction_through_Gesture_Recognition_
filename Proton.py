import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import pyjokes  # Import pyjokes library for generating jokes
import Gesture_Controller
import app
import psutil  # For checking battery status
from threading import Thread
import ctypes  # For checking system volume
import subprocess  # For turning on Bluetooth

# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files = []
path = ''
is_awake = True  # Bot status

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    engine.say(audio)
    engine.runAndWait()

def wish():
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")

    reply("I am Proton, how may I help you?")

# Set Microphone parameters
with sr.Microphone() as source:
    r.energy_threshold = 500
    r.dynamic_energy_threshold = False

# Check Battery Status
def check_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = battery.power_plugged
        charging_status = "charging" if plugged else "not charging"
        reply(f"The battery is at {percent}% and is {charging_status}.")
    else:
        reply("Battery status could not be retrieved. Are you on a desktop?")

# Check System Volume Level
def get_volume():
    devices = ctypes.windll.user32
    # Retrieves the current volume in a range of 0-65535, then we normalize it to a percentage
    class Volume:
        def __init__(self):
            self.vol_min = 0
            self.vol_max = 65535

        def get_current_volume(self):
            waveOutGetVolume = ctypes.windll.winmm.waveOutGetVolume
            volume = ctypes.c_uint32()
            waveOutGetVolume(0, ctypes.byref(volume))
            return volume.value & 0xFFFF

    volume_control = Volume()
    current_volume = volume_control.get_current_volume()

    volume_percentage = int((current_volume / volume_control.vol_max) * 100)
    reply(f"The volume of the system is {volume_percentage} percent.")

# Turn on Bluetooth
def turn_on_bluetooth():
    try:
        # On Windows, enabling Bluetooth through command line using PowerShell
        subprocess.run(["powershell", "-Command", "Start-Service bthserv"], check=True)
        reply("Bluetooth is now turned on.")
    except subprocess.CalledProcessError as e:
        reply(f"Failed to turn on Bluetooth. Error: {str(e)}")

# Open a New Tab in Chrome or Launch Chrome
def open_new_tab():
    # Try to open a new tab if Chrome is already running
    try:
        pyautogui.hotkey('ctrl', 't')  # Simulates CTRL+T to open a new tab
        reply("Opening a new tab in Chrome.")
    except:
        # If Chrome isn't running, launch Chrome
        reply("Chrome was not running, opening Chrome now.")
        webbrowser.get('chrome').open_new('https://google.com')  # Open a new tab with Google

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my service is down. Please check your Internet connection.')
        except sr.UnknownValueError:
            print('Cannot recognize')
            pass
        return voice_data.lower()

# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data = voice_data.replace('proton', '')
    app.eel.addUserMsg(voice_data)

    if is_awake == False:
        if 'wake up' in voice_data:
            is_awake = True
            wish()

    # STATIC CONTROLS
    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Proton!')

    elif 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif 'day' in voice_data:
        today_day = today.strftime("%A")  # Get the current day of the week
        reply(f"Today is {today_day}.")

    elif 'time' in voice_data:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        reply(f"The current time is {current_time}.")

    elif 'search' in voice_data:
        search_term = voice_data.split('search', 1)[1]
        reply('Searching for ' + search_term)
        url = 'https://google.com/search?q=' + search_term
        try:
            webbrowser.get().open(url)
            reply('This is what I found, Sir.')
        except:
            reply('Please check your Internet.')

    elif 'location' in voice_data:
        reply('Which place are you looking for?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/&amp;'
        try:
            webbrowser.get().open(url)
            reply('This is what I found, Sir.')
        except:
            reply('Please check your Internet.')

    elif 'turn on bluetooth' in voice_data:
        turn_on_bluetooth()

    elif 'tell me a joke' in voice_data:
        joke = pyjokes.get_joke()  # Get a random joke
        reply(joke)

    elif 'check battery status' in voice_data:
        check_battery_status()

    elif 'what is the volume level' in voice_data:
        get_volume()

    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active.')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.start()
            reply('Launched Successfully.')

    elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped.')
        else:
            reply('Gesture recognition is already inactive.')

    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied.')

    elif 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted.')

    elif 'play' in voice_data:
        song_name = voice_data.replace('play', '').strip()  # Extract the song name
        reply(f'Playing {song_name} on YouTube.')
        url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
        try:
            webbrowser.get().open(url)
            reply(f"Here is {song_name} on YouTube.")
        except:
            reply('Please check your Internet.')

    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter += 1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory.')
        app.ChatBot.addAppMsg(filestr)

    elif file_exp_status == True:
        counter = 0
        if 'open' in voice_data:
            index = int(voice_data.split(' ')[-1]) - 1
            if isfile(join(path, files[index])):
                os.startfile(join(path, files[index]))
                file_exp_status = False
            else:
                try:
                    path = join(path, files[index]) + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter += 1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened Successfully.')
                    app.ChatBot.addAppMsg(filestr)
                except:
                    reply('You do not have permission to access this folder.')

        elif 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory.')
            else:
                path = os.path.dirname(os.path.dirname(path))
                path += '//'
                files = listdir(path)
                for f in files:
                    counter += 1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('Okay.')
                app.ChatBot.addAppMsg(filestr)

    elif 'bye' in voice_data:
        reply("Goodbye, Sir! Have a nice day.")
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        sys.exit()

    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        sys.exit()

    elif 'open a new tab' in voice_data:
        open_new_tab()

    else:
        reply('I am not functioned to do this!')

# ------------------Driver Code--------------------

t1 = Thread(target=app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        # take input from GUI
        voice_data = app.ChatBot.popUserInput()
    else:
        # take input from Voice
        voice_data = record_audio()

    # process voice_data
    if 'proton' in voice_data:
        try:
            # Handle sys.exit()
            respond(voice_data)
        except SystemExit:
            reply("Exit Successful.")
            break
        except:
            print("Exception raised while closing.")
            break
# At the bottom of Proton.py, encapsulate the main logic
def main():
    t1 = Thread(target=app.ChatBot.start)
    t1.start()

    # Lock main thread until Chatbot has started
    while not app.ChatBot.started:
        time.sleep(0.5)

    wish()
    voice_data = None
    while True:
        if app.ChatBot.isUserInput():
            # take input from GUI
            voice_data = app.ChatBot.popUserInput()
        else:
            # take input from Voice
            voice_data = record_audio()

        # process voice_data
        if 'proton' in voice_data:
            try:
                # Handle sys.exit()
                respond(voice_data)
            except SystemExit:
                reply("Exit Successful.")
                break
            except:
                print("Exception raised while closing.")
                break

# Check if script is run directly
if __name__ == "__main__":
    main()
