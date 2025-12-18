from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def extract_video_id(url):
    # Регулярний вираз для пошуку ID відео
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.post("/info")
async def get_info(request: VideoRequest):
    video_id = extract_video_id(request.url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL"}

    # ПЕРЕВІРТЕ ЦЮ АДРЕСУ: якщо ви підписалися на інший API на RapidAPI, змініть її тут
    api_url = "https://youtube-video-download-info.p.rapidapi.com/dl"
    
    headers = {
        "X-RapidAPI-Key": "d16c4e16fdmsh867bc4e1e4ea9ebp1a6b7cjsn5588224fbd3e",
        "X-RapidAPI-Host": "youtube-video-download-info.p.rapidapi.com"
    }

    try:
        # Спробуємо надіслати тільки ID, як того вимагає більшість API
        response = requests.get(api_url, headers=headers, params={"id": video_id}, timeout=20)
        data = response.json()
        
        # Виводимо в консоль Render для діагностики (ви побачите це в логах)
        print(f"DEBUG API RESPONSE: {data}")

        # Гнучкий пошук посилання у відповіді
        download_url = None
        
        # Спробуємо знайти в полі 'link' (як у YouTube Video Download Info)
        links = data.get("link", {})
        if isinstance(links, dict):
            # Пріоритет: 720p (22) -> 360p (18) -> перше ліпше
            download_url = links.get("22") or links.get("18") or (next(iter(links.values())) if links else None)
        
        # Якщо API іншого типу, посилання може бути в 'url' або 'formats'
        if not download_url:
            download_url = data.get("url") or data.get("downloadUrl")

        if download_url:
            return {
                "success": True,
                "title": data.get("title", "YouTube Video"),
                "thumbnail": data.get("thumb") or data.get("thumbnail") or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                "download_url": download_url
            }
        else:
            return {"success": False, "error": f"API responded but no link found. Raw: {str(data)[:100]}"}

    except Exception as e:
        return {"success": False, "error": f"Server Error: {str(e)}"}
