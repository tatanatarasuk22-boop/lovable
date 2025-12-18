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
    return {"status": "ok"}

@app.post("/info")
async def get_info(request: VideoRequest):
    # Очищаємо посилання від зайвих параметрів трекінгу (?si=...)
    clean_url = request.url.split('?')[0]
    
    COBALT_API = "https://api.cobalt.tools/api/json"
    
    payload = {
        "url": clean_url,
        "vQuality": "720",
        "filenamePattern": "basic",
        "isAudioMuted": False
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.post(COBALT_API, json=payload, headers=headers, timeout=20)
        data = response.json()
        
        # Якщо статус 400, виведемо текст помилки від Cobalt для діагностики
        if response.status_code == 400:
            return {"success": False, "error": f"Cobalt API Error: {data.get('text', 'Invalid link')}"}

        download_url = data.get("url")
        
        if download_url:
            # Витягуємо ID відео для прев'ю
            video_id = ""
            if "v=" in clean_url:
                video_id = clean_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in clean_url:
                video_id = clean_url.split("youtu.be/")[1]

            return {
                "success": True,
                "title": data.get("text", "YouTube Video"),
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
                "download_url": download_url
            }
        
        return {"success": False, "error": "Direct link not found in Cobalt response"}

    except Exception as e:
        return {"success": False, "error": str(e)}
