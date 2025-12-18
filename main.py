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
    return {"status": "ok", "version": "v10-compatible"}

@app.post("/info")
async def get_info(request: VideoRequest):
    # Очищаємо посилання
    clean_url = request.url.split('?')[0]
    
    # НОВИЙ ЕНДПОІНТ Cobalt v10
    COBALT_API = "https://api.cobalt.tools/"
    
    # Новий формат тіла запиту для v10
    payload = {
        "url": clean_url,
        "videoQuality": "720",
        "filenameStyle": "basic"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        # У v10 запит іде на корінь або спеціальний інстанс
        response = requests.post(COBALT_API, json=payload, headers=headers, timeout=20)
        data = response.json()
        
        # У v10 статус може бути 'tunnel', 'redirect' або 'picker'
        if data.get("status") in ["tunnel", "redirect", "success"]:
            video_id = ""
            if "v=" in clean_url:
                video_id = clean_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in clean_url:
                video_id = clean_url.split("youtu.be/")[1]

            return {
                "success": True,
                "title": data.get("text", "YouTube Video"),
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
                "download_url": data.get("url")
            }
        
        return {"success": False, "error": data.get("text", "API Error")}

    except Exception as e:
        return {"success": False, "error": str(e)}
