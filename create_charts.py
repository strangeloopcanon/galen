import os
import time
from openai import OpenAI 
client = OpenAI()

assistant_name = "Slide Generator"
output_file_name = "Chart.png"
assistant_instruction = r"Generate {} file, always. You are a subject-matter expert and create amazing charts. You are incredible at solving difficult data analysis problems. You create beautiful layouts, colors, fonts and styling must be modern and easy to read. Make content engaging. Make the file id available to download.".format(output_file_name)
prompt_user = "Create a perfectly understandable, clear, chart showing the randomized progression of loss functions"
assistant = client.beta.assistants.create(
    name=assistant_name,
    instructions=assistant_instruction,
    tools=[{"type": "code_interpreter"}],
    model="gpt-3.5-turbo-0613")

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=prompt_user)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id)

timeout = 180
interval_time = 5
time_taken = 0
while time_taken < timeout:
    run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id)

    if run.status == 'completed':
        break
    else:
        print(run.status)
        time.sleep(interval_time)
        time_taken += interval_time

messages = client.beta.threads.messages.list(
  thread_id=thread.id)

print(messages)

messages = client.beta.threads.messages.list(thread_id=thread.id)
# After retrieving messages
if all('attachments' not in message or not message['attachments'] for message in messages.data):
    print("No files to download were attached to any messages.")

# Check for file path annotations (although none were found in this case)
has_file_paths = any(
    content.type == 'text' and any(
        annotation.type == 'file_path' for annotation in content.text.annotations
    ) for message in messages.data for content in message.content
)
if not has_file_paths:
    print("No file path annotations found in any messages.")

file_details = {}
file_ids_processed = set()

for message in messages.data:
    if message.role == "assistant":
        for content in message.content:
            if content.type == "image_file":
                file_details[content.image_file.file_id] = "png"
            elif content.type == "text":
                for annotation in content.text.annotations:
                    if annotation.type == "file_path":
                        file_details[annotation.file_path.file_id] = annotation.text.split('.')[-1]

# Download and write the files
for file_id, file_extension in file_details.items():
    # output_file_name = f"Chart.{file_extension}"  # Update file name based on file type
    if file_id not in file_ids_processed:
        file_content = client.files.content(file_id)
        file_data_bytes = file_content.read()
        with open(output_file_name, "wb") as file:
            file.write(file_data_bytes)
        print(f"File saved as {output_file_name}")
        file_ids_processed.add(file_id)
