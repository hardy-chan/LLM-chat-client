from openrouter import OpenRouter
import os

# Load API configuration locally
current_dir = os.getcwd()
file_path = os.path.join(current_dir, "api_key.txt")
with open(file_path, "r") as f:
    my_api_key = f.read().strip()

print("Session initialized. Chat with the assistant. (Type 'exit' to quit)")

# Initialize conversation state
conversation_history = [
#    {"role": "system", "content": "You are a helpful, concise, and friendly AI assistant."}
]

with OpenRouter(api_key=my_api_key) as client:
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Append current user prompt to history for memory within the session
        conversation_history.append({"role": "user", "content": user_input})

        try:
            # Request inference passing the accumulated context window
            response = client.chat.send(
                model="openrouter/free",
                messages=conversation_history,
            )

            ai_response = response.choices[0].message.content
            # Check for safety filter in the response
            if "Response Safety:" in ai_response:
                ai_response = "No response generated due to safety concerns."
            print(f"\nAI: {ai_response}")

            # Append AI response as memory within session
            conversation_history.append({"role": "assistant", "content": ai_response})

        except Exception as e:
            print(f"\nInference Error: {e}")
            conversation_history.pop()  # Rollback state on execution failure
