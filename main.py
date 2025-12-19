import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Дозволяємо запити з вашого домену Lovable
CORS(app)

# Налаштування API
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', 'd16c4e16fdmsh867bc4e1e4ea9ebp1a6b7cjsn5588224fbd3e')
RAPIDAPI_HOST = "youtube-info-and-download-api.p.rapidapi.com"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        # 1. Запит на ініціалізацію завантаження
        # API повертає progress_url
        response = requests.get(
            f"https://{RAPIDAPI_HOST}/download",
            headers=headers,
            params={"id": video_url}
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to contact API", "details": response.text}), response.status_code

        init_data = response.json()
        progress_url = init_data.get('progress_url')

        if not progress_url:
            return jsonify({"error": "No progress URL received from API"}), 500

        # 2. Опитування (Polling) для отримання фінального посилання
        # Робимо до 10 спроб з паузою в 2 секунди
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(2)  # Даємо API час на обробку
            
            progress_response = requests.get(progress_url, headers=headers)
            progress_data = progress_response.json()

            # Якщо посилання готове
            if progress_data.get('download_url'):
                return jsonify({
                    "success": True,
                    "title": init_data.get('title'),
                    "download_url": progress_data.get('download_url'),
                    "thumbnail": init_data.get('info', {}).get('image'),
                    "message": "Video ready!"
                })
            
            # Якщо виникла помилка в самому API під час обробки
            if progress_data.get('error'):
                return jsonify({"error": "API processing error", "details": progress_data}), 500

        return jsonify({"error": "Processing timeout. The video is taking too long."}), 504

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

if __name__ == "__main__":
    # Render використовує порт 10000 за замовчуванням
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
