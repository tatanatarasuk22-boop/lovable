from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/info")
async def get_info(request: VideoRequest):
    # Використовуємо інший дзеркальний інстанс Cobalt на випадок збоїв
    COBALT_API = "https://api.cobalt.tools/api/json"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": request.url,
        "vQuality": "720",
        "filenamePattern": "basic"
    }

    try:
        # Додаємо timeout=15, щоб сервер не "висів" вічно
        response = requests.post(COBALT_API, json=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {"error": f"Cobalt API returned status {response.status_code}"}
            
        data = response.json()
        
        if data.get("status") in ["stream", "redirect", "success"]:
            video_id = ""
            if "v=" in request.url:
                video_id = request.url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in request.url:
                video_id = request.url.split("youtu.be/")[1].split("?")[0]

            return {
                "title": data.get("text", "Video ready"),
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
                "url": data.get("url")
            }
        else:
            return {"error": data.get("text", "Video not found or link unsupported")}
            
    except requests.exceptions.Timeout:
        return {"error": "The request timed out. YouTube is taking too long to respond."}
    except Exception as e:
        return {"error": f"Internal error: {str(e)}"}
