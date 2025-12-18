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
    # Очищаємо ID відео
    video_id = ""
    if "v=" in request.url:
        video_id = request.url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in request.url:
        video_id = request.url.split("youtu.be/")[1].split("?")[0]

    # Використовуємо RapidAPI
    api_url = "https://youtube-video-download-info.p.rapidapi.com/dl"
    headers = {
        "X-RapidAPI-Key": "d16c4e16fdmsh867bc4e1e4ea9ebp1a6b7cjsn5588224fbd3e",
        "X-RapidAPI-Host": "youtube-video-download-info.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params={"id": video_id}, timeout=15)
        data = response.json()
        
        # ЛОГІКА ПОШУКУ ПОСИЛАННЯ:
        # Спершу шукаємо MP4 720p (формат 22), потім будь-яке інше
        link_data = data.get("link", {})
        download_url = ""
        
        if isinstance(link_data, dict):
            # Пробуємо знайти MP4 720p
            download_url = link_data.get("22")
            if not download_url:
                # Якщо немає, беремо перше доступне посилання з масиву
                for key in link_data:
                    if link_data[key]:
                        download_url = link_data[key][0]
                        break

        if download_url:
            return {
                "success": True,
                "title": data.get("title") or "YouTube Video",
                "thumbnail": data.get("thumb") or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                "download_url": download_url
            }
        else:
            return {"success": False, "error": "Could not find a valid download link in the API response."}

    except Exception as e:
        return {"success": False, "error": f"Internal Server Error: {str(e)}"}
