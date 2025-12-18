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

@app.post("/info")
async def get_info(request: VideoRequest):
    # ПРИКЛАД для YouTube/TikTok API з RapidAPI
    url = "https://social-media-video-downloader.p.rapidapi.com/smvd/get/all"
    querystring = {"url": request.url}
    
    headers = {
        "X-RapidAPI-Key": "ВАШ_КЛЮЧ_ТУТ", # <--- ВСТАВТЕ СВІЙ КЛЮЧ
        "X-RapidAPI-Host": "social-media-video-downloader.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        data = response.json()
        
        # Структура відповіді залежить від обраного API на RapidAPI
        return {
            "success": True,
            "title": data.get("title", "Video"),
            "thumbnail": data.get("picture", ""),
            "download_url": data.get("links", [{}])[0].get("link", "")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
