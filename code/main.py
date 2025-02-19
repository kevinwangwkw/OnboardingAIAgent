import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QFrame, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QFont
from openai import OpenAI
import sounddevice as sd
import wave
from scipy.io.wavfile import write
import threading
import requests
from playsound import playsound
import os
import time
from speech_to_text import speech_to_text
from take_screenshot import take_screenshot
from text_to_speech import text_to_speech, play_speech_streaming
from response_generation import generate_text, generate_text_with_image, generate_audio_from_audio
from agent import State, Agent
import whisper
import pyttsx3
from play_audio import play_audio

def get_text(file_path):
    with open(file_path, "r") as file:
        return file.read()

OPENAI_API_KEY = get_text("../api_key.txt").strip()

client = OpenAI(api_key=OPENAI_API_KEY)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: lightgray; border-radius: 10px;")

        #self.setWindowTitle("Naived Onboarding")
        # self.setGeometry(0, 0, 300, 500)  # Initial size, will be adjusted dynamically

        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        width = 300
        height = 500
        x = rect.x() + rect.width() - width
        y = rect.y()
        self.setGeometry(x, y, width, height)

        self.is_recording = False
        self.audio_thread = None

        # Initialize the state variable
        self.state = "intro"

        self.init_ui()

    def init_ui(self):

        # Create frames with labels to display features
        self.feature_texts = [
            "Welcome to Google Docs!"
        ]

        self.feature_frames = []
        for text in self.feature_texts:
            frame = QFrame(self)
            frame.setStyleSheet("background-color: white; border: none; border-radius: 5px;")
            frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)  # Allow frame to expand
            label = QLabel(text, frame)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #333333; background-color: white;")
            label.setWordWrap(True)  # Enable word wrapping
            font = QFont("Arial", 12, QFont.Weight.Bold)
            label.setFont(font)
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)  # Allow label to expand
            layout = QVBoxLayout(frame)
            layout.addWidget(label)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setOffset(2, 2)
            shadow.setColor(QColor(0, 0, 0, 50))
            frame.setGraphicsEffect(shadow)
            self.feature_frames.append((frame, label))  # Store both frame and label

        # Create a single button for recording
        self.record_button = QPushButton("", self)
        self.record_button.setFixedSize(80, 80)

        # self.record_button.setIcon(QIcon("supporting/avatar.png"))
        # self.record_button.setIconSize(QSize(45, 45))
        # self.record_button.setStyleSheet("""
        #     QPushButton {
        #         border-radius: 40px;
        #         background-color: white;
        #         border: 2px solid lightgray;
        #         padding: 0px;
        #     }
        #     QPushButton:pressed {
        #         background-color: #f0f0f0;
        #         border: 2px solid lightgray;
        #         padding: 0px;
        #     }
        # """)
        # Create a container widget for perfect centering
        icon_container = QWidget(self.record_button)
        icon_container.setFixedSize(45, 45)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use QLabel for pixel-perfect icon display
        icon_label = QLabel(icon_container)
        icon_label.setPixmap(QIcon("supporting/avatar.png").pixmap(45, 45))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)

        icon_container.setStyleSheet("background: transparent;")
        icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        
        # Set the container as button's layout
        btn_layout = QVBoxLayout(self.record_button)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)
        btn_layout.addSpacing(10)  # Add vertical space to move the icon slightly downward
        btn_layout.addWidget(icon_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid lightgray;
                border-radius: 40px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:pressed {
                background-color: #f0f0f0;
                border: 2px solid lightgray;
            }
        """)


        button_shadow = QGraphicsDropShadowEffect()
        button_shadow.setBlurRadius(8)
        button_shadow.setOffset(2, 2)
        button_shadow.setColor(QColor(0, 0, 0, 50))
        self.record_button.setGraphicsEffect(button_shadow)
        self.record_button.clicked.connect(self.toggle_recording)

        # Create a layout and add widgets
        self.layout = QVBoxLayout()
        for frame, _ in self.feature_frames:
            self.layout.addWidget(frame)  # Add each feature frame to the layout
        self.layout.addStretch()  # Add stretch to push the button to the lower half

        # Center the button in the lower half
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.record_button)
        button_layout.addStretch()

        self.layout.addLayout(button_layout)
        self.layout.addStretch()  # Add another stretch to push the button to about 3/4 down

        # Set the layout to a container widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Adjust window size based on initial features
        self.adjust_window_size()

    def update_features(self, new_features, callback=None):
        """
        Updates the displayed features with new text.
        """
        # Adjust the number of frames if necessary
        current_count = len(self.feature_frames)
        new_count = len(new_features)

        if new_count > current_count:
            for _ in range(new_count - current_count):
                frame = QFrame(self)
                frame.setStyleSheet("background-color: white; border: none; border-radius: 5px;")
                frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                label = QLabel("", frame)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("color: #333333; background-color: white;")
                label.setWordWrap(True)
                font = QFont("Arial", 12, QFont.Weight.Normal)
                label.setFont(font)
                label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                layout = QVBoxLayout(frame)
                layout.addWidget(label)
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(8)
                shadow.setOffset(2, 2)
                shadow.setColor(QColor(0, 0, 0, 50))
                frame.setGraphicsEffect(shadow)
                self.feature_frames.append((frame, label))
                self.layout.insertWidget(len(self.feature_frames) - 1, frame)
        elif new_count < current_count:
            for _ in range(current_count - new_count):
                frame, label = self.feature_frames.pop()
                self.layout.removeWidget(frame)
                frame.deleteLater()

        for (frame, label), new_text in zip(self.feature_frames, new_features):
            label.setText(new_text)

        self.adjust_window_size()

        # Call the callback if provided
        if callback:
            callback()

    def adjust_window_size(self):
        """
        Adjusts the window size based on the number of feature frames.
        """
        feature_height = 50  # Estimated height for each feature frame
        button_height = 120  # Height for the button and spacing
        total_height = len(self.feature_frames) * feature_height + button_height
        self.setFixedSize(300, total_height)

    def highlight_feature(self, feature_index):
        """
        Highlights the feature at the given index by changing its background color.

        :param feature_index: The index of the feature to highlight (0-based).
        """
        default_frame_style = "background-color: white; border: none; border-radius: 5px; font-weight: normal"
        default_label_style = "color: #333333; background-color: white; border: none;"
        highlight_frame_style = "background-color: white; border: 2px solid blue; border-radius: 5px; font-weight: bold"
        for i, (frame, label) in enumerate(self.feature_frames):
            if i == feature_index:
                frame.setStyleSheet(highlight_frame_style)
                label.setStyleSheet(default_label_style)
            else:
                frame.setStyleSheet(default_frame_style)
                label.setStyleSheet(default_label_style)
        print("highlighted feature: " + str(feature_index))

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        #self.record_button.setText("Stop")

        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

    def stop_recording(self):
        self.is_recording = False
        #self.record_button.setText("Speak")

        if self.audio_thread:
            self.audio_thread.join()

        if agent.state == State.INTRO:
            user_response = str(speech_to_text("supporting/recording.wav", OPENAI_API_KEY))
            option = generate_text(get_text("prompts/options-selection.txt") + user_response, client)
            print("Option selected: " + option)
            if option == "1":
                agent.transition(State.WALKTHROUGH)
            elif option == "2":
                agent.transition(State.SPECIFIC)
            else:
                print("Invalid option")
        elif agent.state == State.WALKTHROUGH:
            user_response = str(speech_to_text("supporting/recording.wav", OPENAI_API_KEY))
            option = generate_text(get_text("prompts/walkthrough-response.txt") + user_response, client)
            if option == "1":
                if agent.check_step():
                    agent.feature_index += 1
                    agent.feature(agent.feature_index)
            else:
                #print("answer question")
                agent.asnwer_question(user_response)

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

    def showEvent(self, event):
        super().showEvent(event)
        # Play the intro audio after the window is shown in a separate thread
    
        threading.Thread(target=self.play_intro_audio).start()
        #self.play_intro_audio()

    def play_intro_audio(self):
        time.sleep(2)  # Wait for 2 seconds before playing the audioct
        #play_audio("prompts/intro-1.txt")

        #playsound("supporting/intro-1.wav")

        playsound("supporting/intro-1.m4a")
        #playsound("supporting/response.wav")

        # engine = pyttsx3.init()
        # engine.setProperty('rate', 155) 
        # engine.say(get_text("prompts/intro-1.txt"))
        # engine.runAndWait()
        #sounddevice.play("supporting/response.wav")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    #text_to_speech(get_text("prompts/intro-1.txt"), client, "supporting/intro-1.wav")
    #text_to_speech(get_text("prompts/intro-2.txt"), client, "supporting/intro-2.wav")

    agent = Agent(window)

    #print("generating text")
    #start_time = time.time()

    # TTS
    #text_to_speech(get_text("prompts/intro-1.txt"), client, "supporting/intro-1.wav") # 4-6s

    # engine = pyttsx3.init()
    # engine.setProperty('rate', 160) 
    # engine.say(get_text("prompts/intro-1.txt"))
    # engine.runAndWait()
    #explaination = generate_text_with_image(get_text("prompts/explain-feature.txt") + "Head to the Google Docs website", "supporting/screenshot.png", client) #5-8s
    #playsound("supporting/intro-1.mp3")


    ### SST
    #speech_to_text("supporting/intro-1.wav", OPENAI_API_KEY) # <1s
    
    #play_speech_streaming(get_text("prompts/intro-1.txt"), client)
    #print("--- %s seconds ---" % (time.time() - start_time))

    sys.exit(app.exec())
