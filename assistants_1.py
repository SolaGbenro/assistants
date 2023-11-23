import openai
import json
import time
import os
from PIL import Image
import io
from dotenv import load_dotenv

# OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Client
client = openai.Client()


def main():

    assistant_id_file = "assistant_1_id.txt"

    # Step 1. Check if file exists
    if os.path.exists(assistant_id_file):
        # read the assistant ID from file
        with open(assistant_id_file, "r") as f:
            assistant_id = f.read().strip()
    else:
        # Create new Assistant
        print("Creating an Assistant...")
        assistant = client.beta.assistants.create(
            name="Math Tutor",
            description="A math tutor assistant",
            instructions="You are a personal math tutor. Write and run code to answer math questions.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4-1106-preview",
        )
        assistant_id = assistant.id

        # write the Assistant ID to a file
        with open(assistant_id_file, "w") as f:
            f.write(assistant_id)
        print(f"Assistant created with ID: {assistant_id}")

    # retrieve the assistant
    assistant = client.beta.assistants.retrieve(assistant_id)
    print(f"Assistant retrieved with ID: {assistant_id}")

    # Step 2. Create a Thread
    print(f"Creating a Thread for a new user conversation...")
    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")

    # Step 3. Add message to Thread
    user_message = "I need to solve the equation `3x + 11 = 14`. Can you help me?"
    print(f"Adding user's message to the Thread, user_message: {user_message}")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    print(f"Message added to the Thread.")

    # Step 4. Run the Assistant
    print(f"Running the assistant to generate a response...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please address the user respectfully. The user requires help with math."
    )
    print(f"Run created with ID: {run.id} and status: {run.status}")

    # Step 5. Display the Assistant's response
    # Continuously check the run status until it's completed
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == 'completed':
            print(f"Run completed. Retrieving the Assistant's responses...")
            break
        print("Waiting for the Assistant to complete the run...")

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    with open("messages.json", "w") as f:
        messages_json = messages.model_dump()
        json.dump(messages_json, f, indent=4)
    print("Displaying the conversation:")
    for msg in messages.data:
        print(f"{msg.role.capitalize()}: {msg.content[0].text.value}")

    # save run steps to json file
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )
    with open("run_steps.json", "w") as f:
        run_steps_json = run_steps.model_dump()
        json.dump(run_steps_json, f, indent=4)


if __name__ == "__main__":
    main()

