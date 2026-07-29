const API_URL = window.location.origin;

const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');

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

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMessage();
});
