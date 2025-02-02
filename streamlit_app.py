import streamlit as st
import requests
import os
import re
from typing import List, Dict
from datetime import datetime

# Constants, set up the Ollama API endpoint and model name
OLLAMA_URL = "http://localhost:11434/api/generate" # local endpoint for the Ollama API
MODEL_NAME = "deepseek-r1:7b" # model name

# Long-Term Memory helper functions
LONG_TERM_MEMORY_FILE = "long_term_memory.txt"

def load_long_term_memory() -> str:
    """Load long-term memory from a text file if it exists."""
    import os
    if os.path.exists(LONG_TERM_MEMORY_FILE):
        with open(LONG_TERM_MEMORY_FILE, "r") as f:
            return f.read()
    return ""

def append_to_long_term_memory(text: str) -> None:
    """Append new conversation to the long-term memory file."""
    with open(LONG_TERM_MEMORY_FILE, "a") as f:
        f.write(text + "\n")

# New helper function to clean assistant response by removing reasoning parts
def clean_assistant_response(response: str) -> str:
    """Remove text between '<think>' and '</think>' markers from the assistant response."""
    import re
    # Use regex to remove text between <think> and </think>
    cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
    return cleaned_response

# Function to generate a response from the LLM
def generate_response(prompt: str, history: List[Dict[str, str]]) -> str:
    """Generate a response from the LLM"""
    # Combine conversation history into a single prompt
    combined_prompt = ""
    for msg in history:
        role_prefix = "User: " if msg["role"] == "user" else "Assistant: "
        combined_prompt += f"{role_prefix}{msg['content']}\n"
    combined_prompt += f"User: {prompt}\nAssistant:"

    # Prepend long-term memory if available
    long_term = load_long_term_memory()
    if long_term:
        combined_prompt = "Long-Term Memory:\n" + long_term + "\n" + combined_prompt
    
    try:
        # Check if Ollama is running
        try:
            requests.head("http://localhost:11434/api/generate", timeout=5)
        except requests.exceptions.RequestException:
            return "Error: Could not connect to Ollama. Please ensure the Ollama service is running."

        # Send the API request to Ollama
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": combined_prompt,
                "stream": False,
                "system": "You are a helpful AI assistant. Provide clear and concise responses. Clarify any unclear or ambiguous information.",
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            },
            timeout=120
        )
        
        # Parse the response
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            return f"Ollama Error: {result['error']}"
        
        # Extract the response text
        response_text = result.get("response", "").strip()
        if not response_text:
            return "I apologize, but I couldn't generate a response. Please try again."
            
        # Return the response text    
        return response_text

    except requests.exceptions.Timeout:
        return "Error: The request timed out. The model is taking too long to respond. You may want to try again with a shorter prompt."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Below are the Streamlit app configuration
st.set_page_config(
    page_title="Local LLM Chat",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("🤖 Local LLM Chat")
st.markdown("Chat with deepseek-r1:7b model served through Ollama")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_response = generate_response(prompt, st.session_state.messages)
            st.markdown(assistant_response)
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Clean the assistant response to remove any reasoning part
            cleaned_response = clean_assistant_response(assistant_response)
            # Append the conversation with timestamp to long-term memory
            conversation_entry = f"{timestamp} - User: {prompt}\n{timestamp} - Assistant: {cleaned_response}"
            append_to_long_term_memory(conversation_entry)
            st.session_state.messages.append({
                "role": "assistant", "content": assistant_response
            })