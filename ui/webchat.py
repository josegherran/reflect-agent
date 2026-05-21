
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
import logging
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import agent

logger = logging.getLogger(__name__)
@app.get("/health")
async def health():
    return {"status": "ok"}

app = FastAPI()

from config import settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "allowed_origins", ["http://localhost:8000"]),
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
    <head><title>ReFlect Agent Webchat</title></head>
    <body>
        <h2>ReFlect Agent Webchat</h2>
        <div id='chat' style='height:300px;overflow:auto;border:1px solid #ccc;padding:10px;'></div>
        <input id='msg' style='width:80%' placeholder='Type your message...'/>
        <button onclick='sendMsg()'>Send</button>
        <script>
        let chat = document.getElementById('chat');
        function sendMsg() {
            let msg = document.getElementById('msg').value;
            if (!msg) return;
            // Use textContent to prevent XSS for user messages
            let userDiv = document.createElement('div');
            userDiv.innerHTML = '<b>You:</b> ';
            let userMsg = document.createElement('span');
            userMsg.textContent = msg;
            userDiv.appendChild(userMsg);
            chat.appendChild(userDiv);
            fetch('/chat', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})})
                .then(r=>r.json()).then(d=>{
                    // TODO: Use DOMPurify or similar to sanitize markdown HTML from agent replies
                    let agentDiv = document.createElement('div');
                    agentDiv.innerHTML = '<b>Agent:</b> ' + d.reply;
                    chat.appendChild(agentDiv);
                    chat.scrollTop = chat.scrollHeight;
                });
            document.getElementById('msg').value = '';
        }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        result = agent(req.message)
        return JSONResponse({"reply": str(result)})
    except Exception:
        logger.exception("Agent call failed")
        return JSONResponse({"error": "Service unavailable"}, status_code=503)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
