import time
from response_generation import generate_text, generate_text_with_image
from text_to_speech import text_to_speech
from take_screenshot import take_screenshot
from openai import OpenAI
from playsound import playsound
import threading
from PyQt6.QtCore import QTimer
import pyttsx3

def get_text(file_path):
    with open(file_path, "r") as file:
        return file.read()

def load_features(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines() if line.strip()]
    
OPENAI_API_KEY = get_text("../api_key.txt").strip()

client = OpenAI(api_key=OPENAI_API_KEY)

class State:
    INTRO = "intro"
    OPTIONS = "options"
    WALKTHROUGH = "walkthrough"
    SPECIFIC = "specific"
    CONFIRM = "confirm"
    COMPLETE = "complete"

class Agent:
    def __init__(self, window):
        self.state = State.INTRO
        self.window = window 
        self.feature_index = 0

    def transition(self, new_state):
        print(f"Transitioning from {self.state} to {new_state}")
        self.state = new_state
        self.handle_state()

    def handle_state(self):
        if self.state == State.INTRO:
            self.introduce()
        elif self.state == State.OPTIONS:
            self.present_options()
        elif self.state == State.WALKTHROUGH:
            self.walkthrough()
        elif self.state == State.SPECIFIC:
            self.specific_problem()
        elif self.state == State.CONFIRM:
            self.confirm()
        elif self.state == State.COMPLETE:
            self.complete()

    def introduce(self):
        # Play introduction audio
        #self.transition(State.OPTIONS)
        return None
    
    def present_options(self):
        # Present options to the user
        # Transition based on user choice
        # user_choice = get_user_choice()  # Implement this function
        # if user_choice == "walkthrough":
        #     self.transition(State.WALKTHROUGH)
        # else:
        #     self.transition(State.SPECIFIC_PROBLEM)
        return None

    def walkthrough(self):
        print("performing walkthrough")
        self.features = load_features("prompts/option1-steps.txt")
        new_features = self.features
        self.window.update_features(new_features, callback=self.on_features_updated)
        #self.window.update_features(new_features, lambda: QTimer.singleShot(0, self.on_features_updated))
        #self.window.update_features(new_features, lambda: self.on_features_updated)

    def on_features_updated(self):
        #self.feature(self.feature_index)
        #threading.Thread(target=self.start_feature_explanation).start()
        self.start_feature_explanation()
        #threading.Thread(target=self.feature(self.feature_index)).start()
        #self.feature_index += 1
        #print(features)
        # for index, feature in enumerate(features):
        #     print(f"Feature {index + 1}: {feature}")
        #     self.window.highlight_feature(0) #index)
        #     self.explain_feature(feature)
        #     # if not self.wait_for_user_confirmation():
        #     #     break
        # self.transition(State.CONFIRM)
    def start_feature_explanation(self):
        self.feature(self.feature_index)

    def feature(self, index):
        if (index >= len(self.features)):
            self.transition(State.COMPLETE)
            return
        #time.sleep(2)
        print(f"Feature {index + 1}: {self.features[index]}")
        self.window.highlight_feature(index)
        self.explain_feature(self.features[index])

        #time.sleep(2)
        #self.feature(index + 1)

    
    def explain_feature(self, feature):
        # Use TTS to explain the feature
        #text_to_speech(f"Let's go through: {feature}", self.client)
        #print("explaining feature: " + feature)
        #option = generate_text(get_text("prompts/walkthrough-response.txt") + user_response, client)

        take_screenshot()
        explanation = generate_text_with_image(get_text("prompts/explain-feature.txt") + feature, "supporting/screenshot.png", client)
        #explanation = feature
        #text_to_speech(explanation, client, "supporting/feature.wav")
        #playsound("supporting/feature.wav")
        engine = pyttsx3.init()
        engine.setProperty('rate', 155) 
        engine.say(explanation)
        engine.runAndWait()

        print("explaining feature: " + feature)

        # prompt, image_path, client
    def asnwer_question(self, text):
        take_screenshot()
        explanation = generate_text_with_image(get_text("prompts/answer-question.txt") + text, "supporting/screenshot.png", client)
        engine = pyttsx3.init()
        engine.setProperty('rate', 155) 
        engine.say(explanation)
        engine.runAndWait()
        print("answering question")

    def specific_problem(self):
        # Address specific problem
        # Transition to confirmation
        #self.transition(State.CONFIRM)
        #return None
        print("performing specific problem")

    def confirm(self):
        # Confirm with the user
        # Transition to completion
        #self.transition(State.COMPLETE)
        return None
    
    def check_step(self):
        take_screenshot()
        explanation = generate_text_with_image(get_text("prompts/confirm-step.txt") + self.features[self.feature_index], "supporting/screenshot.png", client)
        print("check: " + explanation)
        if explanation == "yes" or explanation == "Yes" or explanation == "yes." or explanation == "Yes.":
            engine = pyttsx3.init()
            engine.setProperty("'rate'", 155) 
            engine.say("Great! Let's move on to the next step.")
            engine.runAndWait()   
            return True
        else:   
            engine = pyttsx3.init()
            engine.setProperty('rate', 155) 
            engine.say(explanation)
            engine.runAndWait()                      
        return False

    def complete(self):
        # Complete the onboarding process
        #text_to_speech("You've completed the onboarding...", self.client)
        text = get_text("prompts/end.txt")
        engine = pyttsx3.init()
        engine.setProperty('rate', 155) 
        engine.say(text)
        engine.runAndWait()
        #return None
    
    def wait_for_user_confirmation(self):
        # Wait for user input to confirm or ask questions
        # Implement logic to listen for user input
        # user_input = listen_for_user_input()  # Implement this function
        # if user_input.lower() == "next":
        #     return True
        # elif user_input.lower() == "stop":
        #     return False
        # else:
        #     # Handle questions or other inputs
        #     self.handle_user_question(user_input)
        #     return self.wait_for_user_confirmation()
        return None
    
    def handle_user_question(self, question):
        # Generate a context-aware response
        # context = self.get_context_for_state()
        # prompt = f"{context}\nUser question: {question}"
        # response = generate_text(prompt, self.client)
        # text_to_speech(response, self.client)
        return None

    def get_context_for_state(self):
        # Provide context based on the current state
        # if self.state == State.WALKTHROUGH:
        #     return "We are currently walking through the features."
        # elif self.state == State.SPECIFIC_PROBLEM:
        #     return "We are addressing a specific problem."
        # elif self.state == State.CONFIRMATION:
        #     return "We are confirming your understanding."
        # else:
        #     return "General onboarding assistance."
        return None