import os
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("TUTORIA_MODEL", "llama-3.3-70b-versatile")
WHISPER_MODEL = os.getenv("TUTORIA_WHISPER", "whisper-large-v3-turbo")
_executor = ThreadPoolExecutor(max_workers=2)

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

def _chat_stream(message, context=None, history=None):
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

def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
    ext_map = {
        "audio/webm": "webm",
        "audio/webm;codecs=opus": "webm",
        "audio/ogg": "ogg",
        "audio/ogg;codecs=opus": "ogg",
        "audio/wav": "wav",
        "audio/mp4": "mp4",
        "audio/mpeg": "mp3",
    }
    ext = ext_map.get(mime_type, "webm")
    transcription = client.audio.transcriptions.create(
        file=(f"audio.{ext}", io.BytesIO(audio_bytes)),
        model=WHISPER_MODEL,
        language="es",
    )
    return transcription.text

async def chat_stream_async(message, context=None, history=None):
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    def _run():
        try:
            for chunk in _chat_stream(message, context, history):
                loop.call_soon_threadsafe(queue.put_nowait, chunk)
            loop.call_soon_threadsafe(queue.put_nowait, None)
        except Exception as e:
            loop.call_soon_threadsafe(queue.put_nowait, e)

    loop.run_in_executor(_executor, _run)

    while True:
        item = await queue.get()
        if item is None:
            break
        if isinstance(item, Exception):
            raise item
        yield item
