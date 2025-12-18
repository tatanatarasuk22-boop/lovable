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
    return {"status": "online", "message": "API is working with Cobalt proxy"}

@app.post("/info")
async def get_info(request: VideoRequest):
    # Використовуємо надійний інстанс Cobalt
    COBALT_API = "https://api.cobalt.tools/api/json"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": request.url,
        "vQuality": "720", # можна змінити на 1080
        "filenamePattern": "basic"
    }

    try:
        response = requests.post(COBALT_API, json=payload, headers=headers)
        data = response.json()
        
        # Cobalt повертає пряме посилання в полі 'url'
        if data.get("status") == "stream" or data.get("status") == "redirect":
            return {
                "title": "Video ready",
                "thumbnail": "https://img.youtube.com/vi/" + request.url.split("v=")[-1].split("&")[0] + "/hqdefault.jpg",
                "url": data.get("url")
            }
        else:
            return {"error": data.get("text", "Cobalt error")}
            
    except Exception as e:
        return {"error": str(e)}
