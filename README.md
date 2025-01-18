
# Gifted's AI Chatbot

This project implements a real-time AI chatbot using Python, websockets, and Google's Gemini generative model. It features a sleek and responsive user interface built with HTML, CSS, and JavaScript, providing a seamless chat experience.  The chatbot supports code highlighting with copy-to-clipboard functionality, persistent chat history, error handling, and asynchronous communication for a robust and interactive experience.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)



## Project Description

This AI chatbot aims to provide a user-friendly and efficient way to interact with a powerful language model.  Leveraging the capabilities of Google's Gemini, the chatbot can engage in conversations, answer questions, and generate creative text formats. The server-side logic is implemented in Python using the `websockets` library for real-time communication. The client-side interface, built with HTML, CSS, and JavaScript, offers a modern and responsive design for an optimal user experience across different devices.  The inclusion of code highlighting and a copy-to-clipboard feature enhances the chatbot's utility, especially for technical users.

## Features

- **Real-time communication:**  Uses websockets for instant message exchange between the client and server.
- **AI-powered responses:** Integrates with Google's Gemini generative model for intelligent and context-aware conversations.
- **Code highlighting:**  Employs Pygments to highlight code blocks in various programming languages within the chat, enhancing readability.
- **Copy-to-clipboard:** Allows users to easily copy code snippets from the chat with a dedicated button.
- **Persistent chat history:** Maintains chat history for each user session.
- **Error handling:** Includes robust error handling and informative error messages for both client and server.
- **Asynchronous processing:**  Leverages `asyncio` for efficient handling of concurrent connections and API calls.
- **Responsive design:**  Adapts to different screen sizes for optimal viewing on various devices.
- **Retry mechanism:** Implements retry logic for API calls to handle potential transient errors.
- **Customizable parameters:**  Allows configuration of model parameters like temperature, top_p, and max output tokens.


## Getting Started

### Prerequisites

- **Python 3.7+:** Make sure you have Python installed. You can download it from [python.org](https://www.python.org/).
- **Node.js and npm (optional):**  While not strictly required, having Node.js and npm installed can be useful for running a local development server for the HTML/CSS/JS frontend.
- **Google Cloud Project and API Key:** You'll need a Google Cloud project with the Gemini API enabled and an API key. See [Google Generative AI documentation](https://developers.google.com/generative-ai) for details.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your_username/gifted-ai-chatbot.git  # Replace with your repository URL
   cd gifted-ai-chatbot
   ```
2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv env
   source env/bin/activate  # Activate the environment (Linux/macOS)
   env\Scripts\activate  # Activate the environment (Windows)
   ```
3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Install frontend dependencies (optional):** If you have Node.js and npm, and you've made changes to the frontend code, you can install the frontend dependencies.  While this project doesn't currently have explicit frontend dependencies, this step might be relevant in the future if you add libraries like a JavaScript framework.
    ```bash
    #  npm install  (If any package.json exists in the future)
    ```

### Configuration

1. **Set up environment variables:** Create a `.env` file in the project's root directory and add your Google API key:

   ```
   GOOGLE_API_KEY=YOUR_API_KEY
   ```

2. **Adjust server constants (optional):** Modify the `WEBSOCKET_HOST` and `WEBSOCKET_PORT` constants in `server.py` if needed.

3. **Customize model parameters (optional):**  You can fine-tune the Gemini model's behavior by adjusting parameters like `temperature`, `top_p`, `top_k`, and `max_output_tokens` in the `GENERATION_CONFIG` dictionary in `server.py`.

## Usage

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Open `index.html` in your web browser:** You can either open the file directly or serve it using a local development server (e.g., `python -m http.server` or through a Node.js-based server).  If using a different host/port for the websocket server, make sure to update the websocket URL in the `index.html` JavaScript code.


3. **Start chatting:** Type your messages in the input area and click "Send" or press Enter. The chatbot's responses will appear in the chat window.

## Technologies Used

- **Backend:** Python, `websockets`, `asyncio`, `google-generativeai`, `mistune`, `Pygments`, `dotenv`
- **Frontend:** HTML, CSS, JavaScript, Highlight.js
- **AI Model:** Google Gemini


## Architecture

The chatbot follows a client-server architecture:

- **Client (Web Browser):** The `index.html` file provides the user interface.  It communicates with the server via websockets, sending user messages and receiving bot responses.  The client-side JavaScript handles message rendering, code highlighting using Highlight.js, copy-to-clipboard functionality, and user input.

- **Server (Python):**  The `server.py` file handles websocket connections, receives user messages, interacts with the Gemini API, processes the responses (including Markdown parsing and code highlighting using Pygments), and sends the formatted responses back to the client. It manages chat history per connection and implements error handling and retry mechanisms.

## Contributing

Contributions are welcome!  If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).  You are free to use, modify, and distribute the code as per the terms of the license.  


## Acknowledgements

- This project utilizes Google's Gemini generative model.
- Thanks to the developers of the libraries used: `websockets`, `asyncio`, `google-generativeai`, `mistune`, `Pygments`, `dotenv`, Highlight.js.

## Contact

If you have any questions or need further assistance, feel free to contact [Your Name] at [your_email@example.com].  (Replace with your contact information).
