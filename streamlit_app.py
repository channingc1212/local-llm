import streamlit as st
import requests
import os
from typing import List, Dict

# Constants
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:7b"

def generate_response(prompt: str, history: List[Dict[str, str]]) -> str:
    """Generate a response from the LLM"""
    # Combine conversation history into a single prompt
    combined_prompt = ""
    for msg in history:
        role_prefix = "User: " if msg["role"] == "user" else "Assistant: "
        combined_prompt += f"{role_prefix}{msg['content']}\n"
    combined_prompt += f"User: {prompt}\nAssistant:"

    try:
        # Check if Ollama is running
        try:
            requests.head("http://localhost:11434/api/generate", timeout=5)
        except requests.exceptions.RequestException:
            return "Error: Could not connect to Ollama. Please ensure the Ollama service is running."

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": combined_prompt,
                "stream": False,
                "system": "You are a helpful AI assistant. Provide clear and concise responses.",
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            },
            timeout=120
        )
        
        if response.status_code == 404:
            return f"Error: Model '{MODEL_NAME}' not found. Please ensure you have downloaded it using 'ollama pull {MODEL_NAME}'"
        
        response.raise_for_status()
        
        result = response.json()
        if "error" in result:
            return f"Ollama Error: {result['error']}"
        
        response_text = result.get("response", "").strip()
        if not response_text:
            return "I apologize, but I couldn't generate a response. Please try again."
            
        return response_text

    except requests.exceptions.Timeout:
        return "Error: The request timed out. The model is taking too long to respond. You may want to try again with a shorter prompt."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Page configuration
st.set_page_config(
    page_title="Local LLM Chat",
    page_icon="🤖",
    layout="wide"
)

# Title and description
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
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_response}
            )