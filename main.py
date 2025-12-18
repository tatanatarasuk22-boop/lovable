import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.post("/info")
async def get_info(request: VideoRequest):
    # Використовуємо API Cobalt (open-source), який вміє обходити перевірку на ботів
    cobalt_api = "https://api.cobalt.tools/api/json"
    payload = {
        "url": request.url,
        "vQuality": "720",
        "isAudioOnly": False
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(cobalt_api, json=payload, headers=headers)
        data = response.json()
        
        if data.get("status") == "stream" or data.get("status") == "redirect":
            return {
                "title": "Video Found",
                "url": data.get("url"),
                "thumbnail": "https://img.youtube.com/vi/" + request.url.split("v=")[-1] + "/0.jpg"
            }
        return {"error": "Could not process video"}
    except Exception as e:
        return {"error": str(e)}
