import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Отримуємо ваш робочий ключ із налаштувань Render
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', 'd16c4e16fdmsh867bc4e1e4ea9ebp1a6b7cjsn5588224fbd3e')
RAPIDAPI_HOST = "youtube-info-and-download-api.p.rapidapi.com"

@app.route('/download', methods=['POST'])
def get_download_link():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    # КРОК 1: Ініціалізація завантаження
    try:
        response = requests.get(
            f"https://{RAPIDAPI_HOST}/download",
            headers=headers,
            params={"id": video_url}
        )
        res_data = response.json()

        if not res_data.get('success'):
            return jsonify({"error": "API failed to initialize"}), 500

        # Отримуємо URL для відстеження прогресу
        progress_url = res_data.get('progress_url')
        
        # КРОК 2: Опитування (Polling) прогресу
        # Ми будемо перевіряти статус кожні 2 секунди (макс. 5 спроб)
        for _ in range(5):
            time.sleep(2)
            progress_res = requests.get(progress_url)
            progress_data = progress_res.json()

            # Якщо в прогресі з'явилося готове посилання
            if progress_data.get('download_url'):
                return jsonify({
                    "title": res_data.get('title'),
                    "download_url": progress_data.get('download_url'),
                    "thumbnail": res_data.get('info', {}).get('image')
                })
            
            # Якщо сталася помилка під час обробки
            if progress_data.get('error'):
                break

        return jsonify({"error": "Video processing took too long. Try again."}), 504

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
