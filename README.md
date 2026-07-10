# OpenRouter LLM CLI Client with Oracle DB Logging

A lightweight, secure command-line interface (CLI) client to chat with a large language model (LLM), engineered in Python utilizing the native OpenRouter software development kit (SDK) and backed by an Oracle Database persistence layer.
<img width="1105" height="652" alt="Screenshot-safe" src="https://github.com/user-attachments/assets/8f37213f-b543-4710-a6c3-54f38fd49bea" />

## Features

* **Database-Driven Persistence**: All chat sessions, roles, and message logs are saved permanently on disk with Oracle database.
* **Session Persistence & Retrieval**: Choice to either start a new chat or restore a recent chat session saved in the database.
* **Input Guardrails**: Validates session choices to prevent application crashes and invalid query exceptions.
* **Transactional Error Handling**: Operates with `commit`/`rollback` to ensure data states safety.
* **Flags Handling**: Handles provider safety flags or inference errors by normalizing output or state rollback.
* **Credential Isolation**: Isolates OpenRouter token and Oracle DB root password isolated in external, local text files.
* **Timestamped Spreadsheet Exports**: Automates history extraction in CSV spreadsheet with timestamp-dynamical naming.

## Dependencies & Configuration

Install the required database communication driver and inference SDK:
```bash
pip install oracledb openrouter
```

Initialize access tokens and database passwords within workspace root directory:
```bash
echo YOUR_API_KEY > api_key.txt
echo YOUR_ORACLE_PASSWORD > oracle_pw.txt
```

Set up database schema in Oracle DB instance by running the script: 
* [schema.sql](./schema.sql)

## Operational Execution

### Core Application Client
Launch CLI to start the LLM chatbot:
```bash
python chatbot_oracle.py
```
### Reporting Utilities
To generate history spreadsheets, execute:
```bash
python export.py
```
