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
    return {"status": "ok", "engine": "RapidAPI"}

@app.post("/info")
async def get_info(request: VideoRequest):
    # Використовуємо один з найнадійніших API на RapidAPI
    api_url = "https://youtube-video-download-info.p.rapidapi.com/dl"
    
    # Витягуємо ID відео з посилання
    video_id = ""
    if "v=" in request.url:
        video_id = request.url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in request.url:
        video_id = request.url.split("youtu.be/")[1].split("?")[0]
    
    querystring = {"id": video_id}
    
    headers = {
        "X-RapidAPI-Key": "d16c4e16fdmsh867bc4e1e4ea9ebp1a6b7cjsn5588224fbd3e",
        "X-RapidAPI-Host": "youtube-video-download-info.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring, timeout=15)
        data = response.json()
        
        # Перевіряємо, чи успішна відповідь (статус 200)
        if response.status_code == 200:
            # Цей API зазвичай повертає список форматів у полі 'link'
            links = data.get("link", {})
            # Беремо посилання на 720p або перше доступне
            download_url = links.get("22") or list(links.values())[0][0] if links else ""
            
            return {
                "success": True,
                "title": data.get("title", "YouTube Video"),
                "thumbnail": data.get("thumb", ""),
                "download_url": download_url
            }
        else:
            return {"success": False, "error": f"API Error: {data.get('msg', 'Unknown error')}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}
