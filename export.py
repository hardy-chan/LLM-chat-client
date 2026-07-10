import os, csv, oracledb
from datetime import datetime

timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
file_name = f"chat_history_{timestamp_str}.csv"

# Load DB password
with open(os.path.join(os.getcwd(), "oracle_pw.txt"), "r") as f:
    db_pw = f.read().strip()

# Connect
conn = oracledb.connect(user="system", password=db_pw, dsn="localhost:1521/FREEPDB1")
cursor = conn.cursor()

# Query everything
cursor.execute("SELECT session_id, role, content FROM SYSTEM.chat_history ORDER BY created_at ASC")
rows = cursor.fetchall()

# Write a real spreadsheet file directly to your workspace folder
with open(file_name, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Session ID", "Sender", "Message Text"])
    for sid, role, content in rows:
        text = content.read() if hasattr(content, 'read') else content
        writer.writerow([sid, role, text])

print(f"Spreadsheet successfully created in this folder as '{file_name}'!")
cursor.close()
conn.close()
