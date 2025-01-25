import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sounddevice as sd
import wave
from scipy.io.wavfile import write
import threading
import requests
from speech_to_text import speech_to_text
from take_screenshot import take_screenshot
from text_to_speech import text_to_speech
from openai import OpenAI
from response_generation import generate_text, generate_text_with_image

def get_api_key():
    with open("../api_key.txt", "r") as file:
        return file.read().strip()

OPENAI_API_KEY = get_api_key()

client = OpenAI(api_key=OPENAI_API_KEY)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Onboarding Assistant")
        self.setGeometry(0, 0, 300, 450)

        self.is_recording = False
        self.audio_thread = None

        self.init_ui()

    def init_ui(self):
        self.start_button = QPushButton("Start Recording", self)
        self.start_button.clicked.connect(self.start_recording)

        self.stop_button = QPushButton("Stop Recording", self)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_recording(self):
        self.is_recording = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        if self.audio_thread:
            self.audio_thread.join()

        speech_to_text("supporting/recording.wav", OPENAI_API_KEY)

    def record_audio(self):
        self.filename = "supporting/recording.wav"
        self.samplerate = 44100
        self.channels = 1

        print("Recording started...")
        audio_data = []

        def callback(indata, frames, time, status):
            if status:
                print(f"Sounddevice Status: {status}")
            if self.is_recording:
                audio_data.append(indata.copy())

        with sd.InputStream(samplerate=self.samplerate, channels=self.channels, dtype='int16', callback=callback):
            while self.is_recording:
                sd.sleep(100)

        print("Recording stopped.")
        audio_data = np.concatenate(audio_data, axis=0)

        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.samplerate)
            wf.writeframes(audio_data.tobytes())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()


    #### Test functions

    # Take a screenshot immediately after the window is shown
    #take_screenshot()

    #text_to_speech("Hello, I am your onboarding assistant", client)

    #print("GPT-4o response: ", generate_text("How are you today?", client))

    #print("GPT-4o vision response: ", generate_text_with_image("What is in this image?", "supporting/screenshot.png", client))
    ####

    sys.exit(app.exec())