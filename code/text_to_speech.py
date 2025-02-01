import openai
import os
import time
import sounddevice as sd
import numpy as np
import subprocess
import threading

def text_to_speech(text, client, save_path=None):
    """
    Converts text to speech using OpenAI's tts-1 model and saves the audio to the specified path.

    :param text: The text to be converted to speech.
    :param client: The OpenAI client instance.
    :param save_path: The file path where the audio will be saved.
                      If None, saves to the default "supporting/tts_output.wav".
    """
    if save_path is None:
        # Ensure the supporting directory exists
        os.makedirs("supporting", exist_ok=True)
        save_path = "supporting/tts_output.wav"

    try:
        # Use the OpenAI library to create a TTS request
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )

        # Save the audio content to a file
        with open(save_path, "wb") as audio_file:
            audio_file.write(response.content)
        print(f"Audio saved to {save_path}")

    except Exception as e:
        print(f"Request failed: {e}")

def play_speech_streaming(text, client):
    """
    Streams TTS audio using OpenAI's API, writing to a FIFO pipe and playing it in real time.
    Requires ffplay from the ffmpeg suite.
    """
    fifo_path = "output_pipe.mp3"
    
    # Create a named pipe (FIFO)
    if os.path.exists(fifo_path):
        os.remove(fifo_path)
    os.mkfifo(fifo_path)

    # Create the streaming TTS response
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
    except Exception as e:
        print(f"TTS request failed: {e}")
        os.remove(fifo_path)
        return

    # Define a function that streams audio to the FIFO
    def stream_audio():
        try:
            response.stream_to_file(fifo_path)
        except Exception as e:
            print("Streaming error:", e)

    # Start streaming in a separate thread
    stream_thread = threading.Thread(target=stream_audio, daemon=True)
    stream_thread.start()

    # Use ffplay to play audio from the FIFO in real time.
    # -nodisp: no video window, -autoexit: exit when playback finished, -loglevel panic: suppress debug messages.
    try:
        proc = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-loglevel", "panic", fifo_path])
        proc.wait()
    except Exception as e:
        print("Playback error:", e)

    stream_thread.join()
    os.remove(fifo_path)