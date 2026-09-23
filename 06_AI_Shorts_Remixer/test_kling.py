import os
import sys
import requests
import json
import base64

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

api_key = "api-key-kling-MPNOe3zZkpFIMosfl6r1ITMm_vYxQk-rIgo01uav42o"
img_path = "c:/Users/ktaeh/OneDrive/바탕 화면/안티그래비티/분석실/화산귀환_원본.jpg"

with open(img_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

url = "https://api.klingai.com/v1/videos/image2video"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model_name": "kling-v1",
    "image": b64,
    "prompt": "An epic martial arts swordsman swinging a glowing sharp sword, wind blowing black hair and robe, glowing sword slash aura, battlefield background movement, cinematic anime style",
    "duration": "10",
    "mode": "std"
}

r = requests.post(url, json=payload, headers=headers, timeout=30)
print(f"Status: {r.status_code}")
print(f"Body: {r.text}")
