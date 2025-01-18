import asyncio
import json
import os
import logging
import re
import websockets
import google.generativeai as genai
from dotenv import load_dotenv
import mistune
from websockets.exceptions import ConnectionClosedError
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from typing import Dict, List, Any
import aiohttp  # For asynchronous HTTP requests

# --- Constants and Configuration ---
WEBSOCKET_HOST = "192.168.43.45"  # Use a constant for the host
WEBSOCKET_PORT = 8765             # Use a constant for the port
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO
DEFAULT_LANGUAGE = 'text'
CODE_BLOCK_REGEX = r"```(\w*)\n(.*?)\n```"
MODEL_NAME = "gemini-2.0-flash-exp"
MAX_RETRIES = 3  # Max retries for API calls
RETRY_DELAY = 2 # Retry delay in seconds

# --- Set up logging ---
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

# --- Load environment variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logging.error("GOOGLE_API_KEY not found in environment variables. Please set it.")
    exit(1)  # Exit if API key is missing

genai.configure(api_key=GOOGLE_API_KEY)

# --- Gemini Model Configuration ---
GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# SYSTEM_INSTRUCTION = "You are a highly smart and intelligent chatbot"

SYSTEM_INSTRUCTION = """
You are a helpful chatbot
"""

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=GENERATION_CONFIG,
    system_instruction=SYSTEM_INSTRUCTION,
)

# --- Initialize Mistune and Pygments ---
markdown_parser = mistune.create_markdown()
html_formatter = HtmlFormatter(style='monokai', full=False)

def highlight_code_blocks(text: str) -> str:
    """Highlights code blocks in Markdown using Pygments."""
    def replace_code(match: re.Match) -> str:
        code = match.group(2)
        lang = match.group(1)
        try:
            lexer = get_lexer_by_name(lang) if lang else get_lexer_by_name(DEFAULT_LANGUAGE)
        except:
            lexer = get_lexer_by_name(DEFAULT_LANGUAGE)

        highlighted_code = highlight(code, lexer, html_formatter)
        return f'<pre><code class="language-{lang}">{highlighted_code}</code></pre>'
    return mistune.html(re.sub(CODE_BLOCK_REGEX, replace_code, text, flags=re.DOTALL))

# --- Store chat history per websocket connection ---
chat_histories: Dict[str, List[Dict[str, str]]] = {}


async def generate_response(chat: genai.ChatSession, user_message: str) -> str:
    """Generates a response from the Gemini model with retry logic."""
    for attempt in range(MAX_RETRIES):
      try:
          response = await asyncio.to_thread(chat.send_message, user_message)
          return response.text if response and response.text else "I couldn't generate a response."
      except Exception as e:
          logging.error(f"Error generating content for '{user_message}' (Attempt {attempt+1}): {e}")
          if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(RETRY_DELAY)
          else:
            raise
    return "An error occurred while generating the response"



async def process_message(websocket: websockets.WebSocketClientProtocol, client_address: str, data: Dict[str, Any]):
    """Processes incoming messages and sends a response."""
    action = data.get('action')
    logging.info(f"Received action: {action} from {client_address}")

    if action == 'send_message':
        user_message = data.get('message', '').strip()
        if not user_message:
             await send_error(websocket, "No message provided")
             return

        chat_history = chat_histories.get(client_address, [])
        chat = model.start_chat(history=chat_history)

        try:
          bot_response = await generate_response(chat, user_message)
          html_response = highlight_code_blocks(bot_response)
          response_data = {'type': 'bot', 'message': html_response}
          await websocket.send(json.dumps(response_data))
          chat_histories[client_address] = chat.history

        except Exception as e:
          logging.error(f"Error processing message from {client_address}: {e}")
          await send_error(websocket, "An error occurred while processing your request.")


async def handle_connection(websocket: websockets.WebSocketClientProtocol, path=None):
    """Handles websocket connection."""
    client_address = str(websocket.remote_address)
    logging.info(f"Connection established with {client_address}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await process_message(websocket, client_address, data)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON received from {client_address}: {message}")
                await send_error(websocket, "Invalid JSON data received")
    except ConnectionClosedError:
        logging.info(f"Connection closed for {client_address}")
    except Exception as e:
        logging.error(f"Error during connection with {client_address}: {e}")
    finally:
         if client_address in chat_histories:
            del chat_histories[client_address]



async def send_error(websocket: websockets.WebSocketClientProtocol, message: str):
    """Helper function to send error messages to the client"""
    await websocket.send(json.dumps({'type': 'error', 'message': message}))


async def main():
    async with websockets.serve(handle_connection, WEBSOCKET_HOST, WEBSOCKET_PORT):
        logging.info(f"WebSocket server started on ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        await asyncio.Future()  # Keep server running


if __name__ == "__main__":
    asyncio.run(main())