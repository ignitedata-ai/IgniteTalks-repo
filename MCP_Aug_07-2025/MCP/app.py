import streamlit as st
import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Streamlit page
st.set_page_config(page_title="Personal Agent", layout="centered")
# st.title("📬 Personal Agent")
st.title("🧠 Ignite Agent")

# Set up chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input box
user_input = st.chat_input("Ask me something...")

async def initialize_agent():
    model = ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        openai_api_key=os.getenv("MODEL_API_KEY"),
        temperature=0,
    )

    client = MultiServerMCPClient(
        {
            "weather_agent": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            },
            "email_agent": {
                "url": "http://localhost:8001/mcp",
                "transport": "streamable_http",
            }
        }
    )
    
    tools = await client.get_tools()
    logging.info(tools)
    agent = create_react_agent(model, tools)
    return agent

async def process_user_input(agent, user_input):
    response = await agent.ainvoke({"messages": [{"role": "user", "content": user_input}]})
    return extract_final_tool_message(response)

def extract_final_tool_message(response_dict):
    try:
        messages = response_dict.get("messages", [])
        for msg in reversed(messages):
            if msg.__class__.__name__ == "ToolMessage" and hasattr(msg, "content"):
                return msg.content
            if msg.__class__.__name__ == "AIMessage" and getattr(msg, "content", None):
                return msg.content
    except Exception as e:
        return f"[Error extracting message: {e}]"
    return None

# Run if user submitted input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if "agent" not in st.session_state:
                st.session_state.agent = asyncio.run(initialize_agent())
            response = asyncio.run(process_user_input(st.session_state.agent, user_input))
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})