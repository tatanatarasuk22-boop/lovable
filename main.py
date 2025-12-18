from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# --- НАЛАШТУВАННЯ CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє запити з будь-яких сайтів (включаючи Lovable)
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяє всі методи (GET, POST тощо)
    allow_headers=["*"],  # Дозволяє всі заголовки
)

class VideoRequest(BaseModel):
    url: str

@app.post("/info")
async def get_info(request: VideoRequest):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            return {
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "url": info.get('url'),  # Пряме посилання на відеофайл
                "duration": info.get('duration')
            }
    except Exception as e:
        return {"error": str(e)}
