import requests
import whisper

def speech_to_text(filename, api_key):
    '''
    with open(filename, "rb") as audio_file:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        files = {
            "file": audio_file,
            "model": (None, "whisper-1")
        }
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)

        if response.status_code == 200:
            print("Transcription:", response.json().get("text", ""))
            return response.json().get("text", "")
        else:
            print("Error during transcription:", response.text) 
            return None
    '''
    model = whisper.load_model("tiny.en")
    result = model.transcribe(filename, fp16=False)
    print("transcription: "+ result["text"])
    return result["text"]