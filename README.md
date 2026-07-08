# OpenRouter LLM CLI Client

A lightweight, secure command-line interface (CLI) client to chat with a large language model (LLM), engineered in Python utilizing the native OpenRouter software development kit (SDK). 

## Features

* **Multi-Turn Context Tracking**: Keep memory within session by accumulating messages.
* **Credential Isolation**: Access tokens saved externally in a local file.
* **Flags Handling**: Handle provider safety flags or inference error by normalizing output to user or state rollback.

### Dependency
Install the required upstream SDK:
```bash
pip install openrouter
```

### Configuration
Save token string `API_KEY` into the target file:
```bash
echo API_KEY > api_key.txt
```

