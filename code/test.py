from openai import OpenAI
from response_generation import generate_text_with_image, encode_image

def get_text(file_path):
    with open(file_path, "r") as file:
        return file.read()

OPENAI_API_KEY = get_text("../api_key.txt").strip()

client = OpenAI(api_key=OPENAI_API_KEY)

response = generate_text_with_image("Explain how to change the AI models I could select in Cursor", "supporting/test.png", client)
print(response)
print("\n")

# assistant = client.beta.assistants.create(
#   name="Onboarding Assistant",
#   instructions="You are an expert tech support agent. Use your knowledge base to answer questions about the software, features, and how to use it ",
#   model="gpt-4o",
#   tools=[{"type": "file_search"}],
# )

# vector_store = client.beta.vector_stores.create(name="Software Documentations")
# file_paths = ["supporting/Documentation.pdf"]
# file_streams = [open(path, "rb") for path in file_paths]

# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#   vector_store_id=vector_store.id, files=file_streams
# )

# print(file_batch.status)
# print(file_batch.file_counts)

# assistant = client.beta.assistants.update(
#   assistant_id=assistant.id,
#   tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
# )

#my_assistant = client.beta.assistants.retrieve("asst_57uMLOMnwOfalZa6lHYIzjlN")
#print(my_assistant)

client.files.create(
  file=open("supporting/test.png", "rb"),
  purpose="assistants"
)

file_id = "file-QQpbo2GDtAAe4UPC6gXHHc" #client.files.list()
#print(file_id)

thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=[
                    {"type": "text", "text": "Explain how to change the AI models I could select in Cursor"},
                    {
                        "type": "image_file",
                        "image_file": {
                            "file_id": file_id,
                            "detail": "high"
                        },
                    },
                ]
)

run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id="asst_57uMLOMnwOfalZa6lHYIzjlN",
  instructions="Please answer the user's question based on their screenshot and text; consult documentation if necessary"
)

if run.status == 'completed': 
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  print(messages.data[0].content[0].text.value)
else:
  print(run.status)