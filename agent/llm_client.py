import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = os.getenv("TUTORIA_MODEL", "llama-3.3-70b-versatile")

def _build_messages(message, context=None, history=None):
    messages = []
    if context:
        messages.append({"role": "system", "content": context})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})
    return messages

def chat(message, context=None, history=None):
    messages = _build_messages(message, context, history)
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=1024,
    )
    return response.choices[0].message.content

def chat_stream(message, context=None, history=None):
    messages = _build_messages(message, context, history)
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=1024,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
