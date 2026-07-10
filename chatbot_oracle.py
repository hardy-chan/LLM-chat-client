import os
import oracledb
from openrouter import OpenRouter

# Load OpenRouter API config locally
current_dir = os.getcwd()
file_path_api = os.path.join(current_dir, "api_key.txt")
with open(file_path_api, "r") as f:
    my_api_key = f.read().strip()

# Load Oracle DB config locally
file_path_db = os.path.join(current_dir, "oracle_pw.txt")
with open(file_path_db, "r") as f:
    db_pw = f.read().strip()

# DB connection parameters
DB_USER = os.getenv("DB_USER", "system")
DB_PASSWORD = os.getenv("DB_PASSWORD", db_pw)
DB_DSN = os.getenv("DB_DSN", "localhost:1521/FREEPDB1") 

# DB query limit for context retrieval
DB_LIMIT = 10  # Number of recent messages to fetch for context

def get_db_connection():
    """On-demand thin connection to DB using standard authentication."""
    return oracledb.connect(
        user=DB_USER, 
        password=DB_PASSWORD, 
        dsn=DB_DSN,
    )

def create_chat_session(cursor, session_name: str) -> int:
    """Inserts new session and safely extracts the scalar integer ID from the list."""
    session_id_var = cursor.var(int)
    
    cursor.execute(
        """INSERT INTO SYSTEM.chat_sessions (session_name) 
            VALUES (:name) RETURNING session_id INTO :id""",
        {"name": str(session_name), "id": session_id_var}
    )
    
    # Extract the true raw value from the returned list object
    raw_value = session_id_var.getvalue()
    
    # If Oracle returns it nested like [[1]] or, unwrap it down to a scalar integer
    if isinstance(raw_value, list):
        while isinstance(raw_value, list) and len(raw_value) > 0:
            raw_value = raw_value[0]
            
    return int(raw_value)

def log_message(cursor, session_id: int, role: str, content: str):
    """Saves a message row utilizing safe positional parameters to bypass character array bugs."""
    cursor.execute(
        """INSERT INTO SYSTEM.chat_history (session_id, role, content)
            VALUES (:1, :2, :3)""",
        (int(session_id), str(role), str(content))
    )

def fetch_conversation_context(cursor, session_id: int, limit: int = DB_LIMIT):
    """Queries recent history rows using positional filters and clean tuple unpacking."""
    cursor.execute(
        """SELECT role, content FROM (
               SELECT role, content FROM SYSTEM.chat_history 
               WHERE session_id = :1 
               ORDER BY created_at DESC
           ) WHERE ROWNUM <= :4""",
        (int(session_id), int(limit))
    )
    rows = cursor.fetchall()
    
    # Corrected tuple unpacking logic to read string roles and CLOB contents properly
    return [
        {"role": role, "content": content.read() if hasattr(content, 'read') else content} 
        for role, content in reversed(rows)
    ]


# --- Main Application Workflow ---
try:
    # Initialize connection and session variables
    connection = get_db_connection()
    connection.autocommit = False # control explicit transaction commits
    cursor = connection.cursor()

    print("\n=== System Initialized ===")
    session_title = input("Enter a topic name for this database chat thread: ")
    session_id = create_chat_session(cursor, session_title)
    connection.commit()
    print(f"Secure session registered in Oracle DB under ID: [ {session_id} ]")
    print("Chat with the assistant. (Type 'exit' to quit)")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        if not user_input.strip():
            continue

        # Log user input to DB safely
        try:
            log_message(cursor, session_id, "user", user_input)
            connection.commit()
        except Exception as db_err:
            print(f"\nDatabase Logging Error (User Input): {db_err}")
            connection.rollback()
            continue

        # Fetch context from DB schema for LLM inference
        try:
            conversation_history = fetch_conversation_context(cursor, session_id, limit=DB_LIMIT)
        except Exception as context_err:
            print(f"\nFailed to load memory context from Database: {context_err}")
            conversation_history = [{"role": "user", "content": user_input}]

        # Inference safely via OpenRouter Client
        try:
            with OpenRouter(api_key=my_api_key) as client:
                response = client.chat.send(
                    model="openrouter/free",
                    messages=conversation_history,
                )

            # Process and display AI response, checking for safety filter
            ai_response = response.choices[0].message.content
            if "Response Safety:" in ai_response:
                ai_response = "No response generated due to safety concerns."
            print(f"\nAI: {ai_response}")

            # Log AI output to DB
            log_message(cursor, session_id, "assistant", ai_response)
            connection.commit()

        except Exception as inference_err:
            print(f"\nInference/Execution Error: {inference_err}")
            # Rollback transaction on complete prompt pipeline failure
            connection.rollback() 

except Exception as init_err:
    print(f"Critical Database Connectivity Error: {init_err}")
finally:
    # Always close DB connections to avoid resource leaks
    if 'cursor' in locals(): cursor.close()
    if 'connection' in locals(): connection.close()
    print("\nDatabase connections closed. Session Terminated.")
