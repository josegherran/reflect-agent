from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
            chat.innerHTML += `<div><b>You:</b> ${msg}</div>`;
            fetch('/chat', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})})
                .then(r=>r.json()).then(d=>{
                    chat.innerHTML += `<div><b>Agent:</b> ${d.reply}</div>`;
                    chat.scrollTop = chat.scrollHeight;
                });
            document.getElementById('msg').value = '';
        }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")
    result = agent(user_msg)
    return JSONResponse({"reply": str(result)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
