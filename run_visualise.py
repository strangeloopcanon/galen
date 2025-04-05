import os
import time
import json
import pandas as pd
from openai import OpenAI

def read_json(file_path):
    """
    Read JSON file from the given path and return the data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

dirname = os.getcwd()
config_path = os.path.join(dirname, 'config')
log_path = os.path.join(dirname, 'logs')
output_directory = "output"

info = read_json(os.path.join(config_path, 'info.json'))
GPT_MODEL = info.get('GPT_4')

def visualize(results_df):
    client = OpenAI()

    # Define assistant settings
    assistant_name = "Slide Generator"
    os.makedirs(output_directory, exist_ok=True)
    file_name = "Chart.png"
    output_file_name = os.path.join(output_directory, file_name)
    assistant_instruction = (
        r"Generate {} file, always. You are a subject-matter expert and create amazing charts."
        r"You are incredible at solving difficult data analysis problems. You create beautiful layouts, colors, fonts, "
        r"and styling must be modern and easy to read. Make content engaging. Make the file id available to download."
        .format(output_file_name)
    )

    # Serialize DataFrame to CSV for message passing
    # results_df_csv = results_df.to_csv(index=False)

    # Update prompt to include DataFrame usage
    prompt_user = (
        "Create a perfectly understandable, clear, chart. Here is the data you need to visualize:\n" + results_df.to_string()
    )

    # Create an assistant
    assistant = client.beta.assistants.create(
        name=assistant_name,
        instructions=assistant_instruction,
        tools=[{"type": "code_interpreter"}],
        model=GPT_MODEL)

    # Create a thread
    thread = client.beta.threads.create()

    # Create a message
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt_user)

    # Start the run
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id)

    # Wait for the run to complete
    timeout = 560
    interval_time = 5
    time_taken = 0
    while time_taken < timeout:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)

        if run.status == 'completed':
            break
        elif run.status == 'failed':
            print("Run failed.")
            return
        else:
            print(run.status)
            time.sleep(interval_time)
            time_taken += interval_time

    # Retrieve messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    for message in messages.data:
        print(f"message so far is: {message}")
        file_id = get_file_id_from_message(message)
        file_content = client.files.content(file_id)
        file_data_bytes = file_content.read()
        with open(output_file_name, "wb") as file:
            file.write(file_data_bytes)
        print(f"File saved as {output_file_name}")
        return

    print("No files were generated or saved.")

def get_file_id_from_message(message):
    if message.content and hasattr(message.content[0], 'image_file'):
        return message.content[0].image_file.file_id
    elif message.attachments and hasattr(message.attachments[0], 'file_id'):
        return message.attachments[0].file_id
    else:
        return None

if __name__ == "__main__":
    # Example DataFrame
    results_df = pd.DataFrame({
        'Epoch': [1, 2, 3, 4, 5],
        'Loss': [0.4, 0.35, 0.3, 0.25, 0.2]
    })
    visualize(results_df)