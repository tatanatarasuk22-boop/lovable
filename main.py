from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

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
    return {"status": "ok", "info": "Use POST /info for downloads"}

@app.post("/info")
async def get_info(request: VideoRequest):
    COBALT_API = "https://api.cobalt.tools/api/json"
    payload = {
        "url": request.url,
        "vQuality": "720",
        "filenamePattern": "basic"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(COBALT_API, json=payload, headers=headers, timeout=20)
        data = response.json()
        
        # Перевіряємо всі можливі поля, де може бути посилання
        download_url = data.get("url") or data.get("link") or data.get("stream")
        
        if download_url:
            # Витягуємо ID відео для прев'ю
            video_id = ""
            if "v=" in request.url:
                video_id = request.url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in request.url:
                video_id = request.url.split("youtu.be/")[1].split("?")[0]

            return {
                "success": True,
                "title": "Your Video is Ready",
                "download_url": download_url, # Чітке ім'я поля для Lovable
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else ""
            }
        else:
            return {"success": False, "error": "Download link not found in API response", "raw_data": data}

    except Exception as e:
        return {"success": False, "error": str(e)}
