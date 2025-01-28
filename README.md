# Local LLM Chat Application

A simple chat interface for interacting with the DeepSeek-R1:7B model locally through Ollama.

## Prerequisites

1. Install [Ollama](https://ollama.ai/)
2. Pull the DeepSeek-R1:7B model:
```bash
ollama pull deepseek-r1:7b
```
3. Python 3.8+ installed on your system

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd local-llm
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure Ollama is running in the background with the DeepSeek-R1:7B model pulled.

2. Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

3. The chat interface will open in your default web browser (typically at http://localhost:8501)

4. Type your message in the input box and press Enter to chat with the model.

## Features

- Clean and simple chat interface
- Real-time responses from the DeepSeek-R1:7B model
- Conversation history maintained throughout the session
- Error handling for common issues (model not found, Ollama not running, etc.)
- System prompt to guide model behavior
- Configurable model parameters (temperature, top_p, top_k)

## Troubleshooting

1. If you see "Could not connect to Ollama" error:
   - Make sure Ollama is running
   - Check if the model is properly downloaded using `ollama list`

2. If responses are slow:
   - This is normal for the first few requests as the model loads into memory
   - Subsequent requests should be faster

3. If you encounter other issues:
   - Check the terminal output for error messages
   - Ensure all prerequisites are properly installed
   - Try restarting both Ollama and the Streamlit app

## Contributing

Feel free to open issues or submit pull requests for any improvements you'd like to suggest.

## License

[MIT License](LICENSE)
