import openai
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def generate_text(prompt, client):
    """
    Generates text output using OpenAI's GPT-4o model.

    :param prompt: The language prompt to be processed.
    :param client: The OpenAI client instance.
    :return: The generated text output.
    """
    try:
        # Use the OpenAI library to create a text generation request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}
            ],
            
        )

        # Extract and return the generated text
        return response.choices[0].message.content

    except Exception as e:
        print(f"Request failed: {e}")
        return None

def generate_text_with_image(prompt, image_path, client):
    """
    Generates text output using OpenAI's GPT-4o Vision model with an image.

    :param prompt: The language prompt to be processed.
    :param image_path: The path to the image file.
    :param client: The OpenAI client instance.
    :return: The generated text output.
    """
    try:
        # Encode the image file
        encoded_image = encode_image(image_path)
        
        # Use the OpenAI library to create a vision request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}",
                        },
                    },
                ]
                }
            ],
        )

        # Extract and return the generated text
        return response.choices[0].message.content

    except FileNotFoundError:
        print(f"Image file not found: {image_path}")
        return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None 
    
def encode_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode("utf-8")

def generate_audio_from_audio(input_path, output_path, client):
    """
    Generates an audio response from an audio input using OpenAI's GPT-4o-audio API.

    :param input_path: The path to the input audio file.
    :param output_path: The path where the output audio will be saved.
    :param client: The OpenAI client instance.
    """
    try:
        # Encode the input audio file
        encoded_audio = encode_audio(input_path)

        # Create a request to the GPT-4o-audio API
        completion = client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=['text', "audio"],
            audio={"voice": "alloy", "format": "wav"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": encoded_audio,
                                "format": "wav"
                            }
                        }
                    ]
                }
            ]
        )

        # Decode the response audio and save it to the output path
        wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        with open(output_path, "wb") as f:
            f.write(wav_bytes)
        print(f"Audio response saved to {output_path}")

    except FileNotFoundError:
        print(f"Input audio file not found: {input_path}")
    except Exception as e:
        print(f"Request failed: {e}")

# def generate_audio_from_audio_image(image_path, audio_path, output_path, client):
#     try:
#         # Encode the input audio file
#         encoded_audio = encode_audio(audio_path)
#         encoded_image = encode_image(image_path)

#         # Create a request to the GPT-4o-audio API
#         completion = client.chat.completions.create(
#             model="gpt-4o-audio-preview",
#             modalities=['text', "audio", "image"],
#             audio={"voice": "alloy", "format": "wav"},
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "input_audio",
#                             "input_audio": {
#                                 "data": encoded_audio,
#                                 "format": "wav"
#                             }
#                         },
#                         {
#                             "type": "image_url",
#                             "image_url": {
#                                 "url": f"data:image/png;base64,{encoded_image}",
#                             }
#                         }
#                     ]
#                 }
#             ]
#         )

#         # Decode the response audio and save it to the output path
#         wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
#         with open(output_path, "wb") as f:
#             f.write(wav_bytes)
#         print(f"Audio response saved to {output_path}")

#     except FileNotFoundError:
#         print(f"Input audio file not found: {audio_path}")
#     except Exception as e:
#         print(f"Request failed: {e}")