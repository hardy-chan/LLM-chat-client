from openrouter import OpenRouter
import os

# Read API key from file
current_dir = os.getcwd()
file_path = os.path.join(current_dir, "api_key.txt")
with open(file_path, "r") as f:
    my_api_key = f.read().strip()

print("Hello World, LLM! What would you like to ask the AI? (Type 'exit' to quit)")

# User-AI interaction loop

with OpenRouter(api_key = my_api_key) as client:
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        response = client.chat.send(
            model="openrouter/auto",
            messages=[
                {"role": "user", "content": user_input}
            ],
        )

        print(response.choices[0].message.content)