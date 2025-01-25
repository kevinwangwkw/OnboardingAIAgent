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
    

