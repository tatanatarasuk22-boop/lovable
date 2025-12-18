from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Дозволяємо Lovable підключатися до нашого сервера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

# Це виправить помилку 404, коли ви просто відкриваєте посилання в браузері
@app.get("/")
async def root():
    return {"message": "API is online and ready for Lovable!"}

@app.post("/info")
async def get_info(request: VideoRequest):
    # Використовуємо Cobalt API, щоб обійти блокування YouTube
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
        response = requests.post(COBALT_API, json=payload, headers=headers)
        data = response.json()
        
        if data.get("status") == "stream" or data.get("status") == "redirect":
            # Спробуємо дістати ID відео для прев'ю
            video_id = ""
            if "v=" in request.url:
                video_id = request.url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in request.url:
                video_id = request.url.split("youtu.be/")[1].split("?")[0]

            return {
                "title": "Video ready",
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
                "url": data.get("url")
            }
        else:
            return {"error": data.get("text", "Cobalt could not process this link")}
            
    except Exception as e:
        return {"error": str(e)}
