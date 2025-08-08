# 🧠 IgniteAI Agent using Model Context Protocol (MCP)

This proof of concept demonstrates Model Context Protocol (MCP) integration with multiple tools in a single application.

## Current Features

- 📧 **Email Tool**: Reads unread Gmail messages and replies to them.
- ☀️ **Weather Tool**: Fetches real-time weather information for a given location.

The system is built to scale — you can easily add new tools by creating their own MCP server and registering them in the app.

## Steps to Run

### Step 0: Install Python & Dependencies

Ensure you have Python 3.11.9 installed.

Install all dependencies:

```bash
pip install -r requirements.txt
```
#### Note: Switch on to MCP directory, before running any commands for this demo

### Step 1: Gmail API Setup

Enable the Gmail API in your Google Cloud console and download the credentials file.

### Step 2: Environment Variables

Ensure to change the values for the following keys in .env file

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini  # or any model of your choice
```

### Step 3: Run the MCP Servers

**Email MCP Server** (Port 8000)

```bash
python mcp_email_server.py
```

**Weather MCP Server** (Port 8001)

```bash
python mcp_weather_server.py
```

### Step 4: Run the Streamlit App

In a new terminal:

```bash
streamlit run app.py
```

### Step 5: Adding New Tools

You can scale up to as many tools as you like:

1. Create a new MCP server script:

```bash
mcp_new_tool_server.py
```

2. Add the server configuration in `app.py`:

```python
client = MultiServerMCPClient(
    {
        "weather_agent": {
            "url": "http://localhost:8001/mcp",
            "transport": "streamable_http"
        },
        "email_agent": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http"
        },
        "new_tool": {
            "url": "http://localhost:8002/mcp",
            "transport": "streamable_http"
        }
    }
)
```

## Notes

MCP allows us to connect **N LLMs** to **M Tools** without the **N × M** integration complexity — instead, we only need **N + M** connections.

This makes tool integration more scalable, consistent, and reliable.