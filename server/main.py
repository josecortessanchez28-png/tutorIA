from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from agent.llm_client import chat
from agent.prompts import SYSTEM_PROMPT

app = FastAPI(title="TutorIA", version="0.1.0")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    response = chat(req.message, context=SYSTEM_PROMPT)
    return {"response": response}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
