const API_URL = window.location.origin;
const WS_URL = API_URL.replace(/^http/, 'ws') + '/ws';

const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');

let currentBubble = null;

function addMessage(text, isUser) {
  const div = document.createElement('div');
  div.className = `message ${isUser ? 'user' : 'bot'}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = isUser ? 'U' : 'T';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;

  div.appendChild(avatar);
  div.appendChild(bubble);
  chatArea.appendChild(div);
  chatArea.scrollTop = chatArea.scrollHeight;
  return bubble;
}

function showTyping() {
  typingIndicator.classList.remove('hidden');
  chatArea.scrollTop = chatArea.scrollHeight;
}

function hideTyping() {
  typingIndicator.classList.add('hidden');
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, true);
  userInput.value = '';
  showTyping();

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    hideTyping();
    addMessage(data.response, false);
  } catch (err) {
    hideTyping();
    addMessage('Error de conexión. Intenta de nuevo.', false);
  }
}

let ws = null;
let wsQueue = [];

function connectWebSocket() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => {
    for (const msg of wsQueue) {
      ws.send(JSON.stringify({ message: msg }));
    }
    wsQueue = [];
  };
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.chunk) {
      if (!currentBubble) {
        hideTyping();
        currentBubble = addMessage('', false);
      }
      currentBubble.textContent += data.chunk;
      chatArea.scrollTop = chatArea.scrollHeight;
    }
    if (data.done) {
      currentBubble = null;
      hideTyping();
    }
    if (data.error) {
      currentBubble = null;
      hideTyping();
      addMessage('Error: ' + data.error, false);
    }
  };
  ws.onclose = () => {};
}

function sendMessageStream() {
  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, true);
  userInput.value = '';
  showTyping();
  currentBubble = null;

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ message: text }));
  } else {
    wsQueue.push(text);
    if (!ws || ws.readyState === WebSocket.CLOSED) {
      connectWebSocket();
    }
  }
}

connectWebSocket();

sendBtn.addEventListener('click', sendMessageStream);

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMessageStream();
});
