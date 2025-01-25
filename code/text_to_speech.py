import openai
import os

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

    except openai.error.OpenAIError as e:
        print(f"Request failed: {e}")