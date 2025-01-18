// server.js
const WebSocket = require('ws');
const http = require('http');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const dotenv = require('dotenv');
const MarkdownIt = require('markdown-it');
const hljs = require('highlight.js');

dotenv.config();

const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
const WEBSOCKET_PORT = 8765;
const WEBSOCKET_HOST = '192.168.17.45'; // Using localhost for local testing

if (!GOOGLE_API_KEY) {
    console.error('GOOGLE_API_KEY not found in environment variables. Please set it.');
    process.exit(1);
}

const genAI = new GoogleGenerativeAI(GOOGLE_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash-exp" });

const generationConfig = {
    temperature: 1,
    topP: 0.9,
    topK: 40,
    maxOutputTokens: 8192,
};

const systemInstruction = "I will give you a project topic and you are to generate a very very long and elaborate project document for it starting from the table of contents, you are to do it step by step and chapter by chapter";

const chatHistories = new Map();

const server = http.createServer();
const wss = new WebSocket.Server({ noServer: true });

// Configure markdown-it with syntax highlighting
const md = new MarkdownIt({
    highlight: (str, lang) => {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(str, { language: lang }).value;
            } catch (__) {}
        }
        return ''; // Use default escaping if no language is provided
    }
});

async function generateResponse(chat, userMessage) {
    try {
        const result = await chat.sendMessage(userMessage);
        const response = result.response;
        return response.text();
    } catch (error) {
        console.error('Error generating response:', error);
        return "I couldn't generate a response.";
    }
}

wss.on('connection', ws => {
    const clientAddress = ws._socket.remoteAddress + ':' + ws._socket.remotePort;
    console.log(`Connection established with ${clientAddress}`);
    chatHistories.set(clientAddress, model.startChat({
        generationConfig: generationConfig,
        systemInstruction: {
            parts: [{ text: systemInstruction }]
        },
        history: [],
    }));

    ws.on('message', async messageString => {
        try {
            const data = JSON.parse(messageString);
            const action = data.action;

            if (action === 'send_message') {
                const userMessage = data.message?.trim();
                if (!userMessage) {
                    sendError(ws, 'No message provided');
                    return;
                }

                const chat = chatHistories.get(clientAddress);
                if (!chat) {
                    console.error(`Chat history not found for ${clientAddress}`);
                    sendError(ws, 'Chat session error.');
                    return;
                }

                try {
                    const botResponse = await generateResponse(chat, userMessage);
                    const htmlResponse = md.render(botResponse);
                    const responseData = { type: 'bot', message: htmlResponse };
                    ws.send(JSON.stringify(responseData));
                } catch (error) {
                    console.error('Error processing message:', error);
                    sendError(ws, 'An error occurred while processing your request.');
                }
            }
        } catch (error) {
            console.error('Error processing message:', error);
            sendError(ws, 'Invalid message format.');
        }
    });

    ws.on('close', () => {
        console.log(`Connection closed for ${clientAddress}`);
        chatHistories.delete(clientAddress);
    });

    ws.on('error', error => {
        console.error(`WebSocket error for ${clientAddress}:`, error);
        chatHistories.delete(clientAddress);
    });
});

function sendError(ws, message) {
    ws.send(JSON.stringify({ type: 'error', message: message }));
}

server.on('upgrade', (request, socket, head) => {
    wss.handleUpgrade(request, socket, head, ws => {
        wss.emit('connection', ws, request);
    });
});

server.listen(WEBSOCKET_PORT, WEBSOCKET_HOST, () => {
    console.log(`WebSocket server started on ws://${WEBSOCKET_HOST}:${WEBSOCKET_PORT}`);
});
