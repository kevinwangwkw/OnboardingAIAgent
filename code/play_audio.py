import pyttsx3
import threading

engine = pyttsx3.init()
engine.setProperty('rate', 155) 

def get_text(file_path):
    with open(file_path, "r") as file:
        return file.read()

def play_audio(filename):
    def speak():
        engine.say(get_text(filename))
        engine.runAndWait()
    thread = threading.Thread(target=speak, daemon=True)
    thread.start()