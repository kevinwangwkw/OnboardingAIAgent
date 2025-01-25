import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt
from openai import OpenAI
import sounddevice as sd
import wave
from scipy.io.wavfile import write
import threading
import requests
from speech_to_text import speech_to_text
from take_screenshot import take_screenshot
from text_to_speech import text_to_speech
from response_generation import generate_text, generate_text_with_image, generate_audio_from_audio

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
        
        # Create frames with labels to display features
        self.feature_texts = [
            "Feature 1: Speech to Text",
            "Feature 2: Text to Speech",
            "Feature 3: Screenshot",
            "Feature 4: Audio Generation"
        ]

        self.feature_frames = []
        for text in self.feature_texts:
            frame = QFrame(self)
            frame.setStyleSheet("background-color: gray; border: none; border-radius: 10px;")
            label = QLabel(text, frame)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: white;")
            layout = QVBoxLayout(frame)
            layout.addWidget(label)
            self.feature_frames.append(frame)

        # Create a single button for recording
        self.record_button = QPushButton("Speak", self)
        self.record_button.setFixedSize(100, 100)  # Set fixed size for the button
        self.record_button.setStyleSheet("""
            QPushButton {
                border-radius: 50px;  /* Half of the width/height to make it circular */
                background-color: #4CAF50;  /* Green background */
                color: white;
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: #45a049;  /* Darker green when pressed */
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)

        # Create a layout and add widgets
        layout = QVBoxLayout()
        for frame in self.feature_frames:
            layout.addWidget(frame)  # Add each feature frame to the layout
        layout.addStretch()  # Add stretch to push the button to the lower half

        # Center the button in the lower half
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.record_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()  # Add another stretch to push the button to about 3/4 down

        # Set the layout to a container widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def highlight_feature(self, feature_index):
        """
        Highlights the feature at the given index by changing its background color.

        :param feature_index: The index of the feature to highlight (0-based).
        """
        for i, frame in enumerate(self.feature_frames):
            if i == feature_index:
                frame.setStyleSheet("background-color: blue; border: none; border-radius: 10px;")
            else:
                frame.setStyleSheet("background-color: gray; border: none; border-radius: 10px;")

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.setText("Stop")

        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.setText("Speak")

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

    # Example usage: Highlight the first feature
    window.highlight_feature(0)

    sys.exit(app.exec())