import os
import sys
import time
import base64
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv(dotenv_path="c:/Users/ktaeh/OneDrive/바탕 화면/안티그래비티/06_AI_Shorts_Remixer/.env")

from core.tts_engine import TTSEngine
from core.sound_engine import SoundFXEngine

def make_cinematic_motion_video(img_path: str, output_path: str, duration=10.0, fps=30):
    """Kling API 대기/백업 겸용 10초 시네마틱 패닝/줌인 모션 비디오 렌더러"""
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance
    from moviepy import ImageClip, CompositeVideoClip, AudioFileClip

    img = Image.open(img_path).convert("RGB")
    orig_w, orig_h = img.size
    
    target_w, target_h = 1080, 1920
    
    # 세로 9:16 맞춤 리사이즈 베이스
    scale = max(target_w / orig_w, target_h / orig_h) * 1.15
    nw, nh = int(orig_w * scale), int(orig_h * scale)
    base_img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    
    # 줌인 & 시네마틱 애니메이션 프레임 생성
    def make_frame(t):
        progress = t / duration # 0.0 ~ 1.0
        # 부드러운 줌인 (1.0 -> 1.18) 및 인물 얼굴/검 쪽으로 미세 패닝
        zoom = 1.0 + 0.18 * np.sin(progress * np.pi / 2)
        cur_w, cur_h = int(target_w * zoom), int(target_h * zoom)
        
        # 인물 눈과 검에 포커스되는 크롭
        x_center = int(nw * (0.5 + 0.03 * (1 - progress)))
        y_center = int(nh * (0.45 + 0.04 * progress))
        
        x1 = max(0, x_center - cur_w // 2)
        y1 = max(0, y_center - cur_h // 2)
        x2 = min(nw, x1 + cur_w)
        y2 = min(nh, y1 + cur_h)
        
        cropped = base_img.crop((x1, y1, x2, y2)).resize((target_w, target_h), Image.Resampling.BILINEAR)
        frame_np = np.array(cropped)
        
        # 검광/빛 번쩍임 효과 (2초, 5초, 8초 시점에 미세 플래시)
        flash_intensity = 0
        for f_time in [1.5, 4.5, 7.5]:
            if abs(t - f_time) < 0.25:
                flash_intensity = max(flash_intensity, (1.0 - abs(t - f_time) / 0.25) * 40)
        
        if flash_intensity > 0:
            frame_np = np.clip(frame_np.astype(np.int16) + int(flash_intensity), 0, 255).astype(np.uint8)
            
        return frame_np

    # MoviePy 비디오 클립 생성
    from moviepy import VideoClip
    clip = VideoClip(make_frame, duration=duration)
    return clip

def run_image_to_video():
    img_path = "c:/Users/ktaeh/OneDrive/바탕 화면/안티그래비티/분석실/화산귀환_원본.jpg"
    out_dir = "c:/Users/ktaeh/OneDrive/바탕 화면/안티그래비티/분석실/분석실완료"
    os.makedirs(out_dir, exist_ok=True)
    final_output = os.path.join(out_dir, "화산귀환_10초_시네마틱_쇼츠.mp4")

    print("==================================================")
    print("⚔️ 화산귀환 10초 시네마틱 AI 영상 제작 가동")
    print("==================================================")

    # 1. 웅장한 무협 대본 작성 & ElevenLabs 한국어 더빙
    script = "천년의 검맥이 깨어난다. 화산의 이름으로, 단 한 번의 검으로 모든 것을 벨 것이다!"
    print(f"\n[1/3] 🎙️ ElevenLabs 나레이션 음성 생성: \"{script}\"")
    
    tts = TTSEngine()
    temp_dir = "c:/Users/ktaeh/OneDrive/바탕 화면/안티그래비티/06_AI_Shorts_Remixer/temp"
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, "hwasan_voice.mp3")
    tts.generate_speech(script, audio_path)

    # 2. Kling AI API 호출 시도 (Image-to-Video)
    kling_key = os.getenv("KLING_API_KEY")
    kling_success = False
    kling_video_path = os.path.join(temp_dir, "kling_hwasan.mp4")

    if kling_key:
        try:
            print("\n[2/3] 🤖 Kling AI Image-to-Video 생성 요청 중...")
            with open(img_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")

            url = "https://api.klingai.com/v1/videos/image2video"
            headers = {
                "Authorization": f"Bearer {kling_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "kling-v1",
                "image": img_b64,
                "prompt": "검을 쥐고 정면을 응시하는 무림 고수, 도포와 검은 머리카락이 바람에 휘날림, 검날에 푸른 검기가 번뜩이고 배경의 화산파 성채에 구름이 흐름, 4k 시네마틱 무협 액션",
                "duration": "10",
                "mode": "std"
            }
            res = requests.post(url, json=payload, headers=headers, timeout=20)
            data = res.json()
            if res.status_code == 200 and data.get("code") == 0:
                task_id = data.get("data", {}).get("task_id")
                print(f"[Kling AI] 생성 작업 등록 성공 (Task ID: {task_id}). 렌더링 확인...")
                # Polling
                from core.kling_client import KlingAIClient
                client = KlingAIClient(api_key=kling_key)
                downloaded = client.wait_and_download_video(task_id, kling_video_path, max_wait_sec=120)
                if downloaded and os.path.exists(downloaded):
                    kling_success = True
            else:
                print(f"[Kling AI] 응답: {data}")
        except Exception as e:
            print(f"[Kling AI] Image-to-Video API 요청 실패: {e}")

    # 3. 비디오 클립 생성 (Kling 또는 고성능 시네마틱 모션 엔진)
    from moviepy import VideoFileClip, CompositeVideoClip, AudioFileClip
    if kling_success and os.path.exists(kling_video_path):
        print("\n[3/3] 🎬 Kling AI 생성 비디오 기반 최종 합성...")
        base_clip = VideoFileClip(kling_video_path).with_duration(10.0)
    else:
        print("\n[3/3] 🎬 초고화질 시네마틱 다이내믹 모션 엔진으로 10초 영상 렌더링...")
        base_clip = make_cinematic_motion_video(img_path, final_output, duration=10.0)

    # 사운드트랙 (더빙 + 검기 효과음 + 웅장한 사운드)
    sound_engine = SoundFXEngine(temp_dir=temp_dir)
    soundtrack = sound_engine.build_mixed_soundtrack(
        narration_path=audio_path,
        cut_times=[1.5, 4.5, 7.5],
        total_duration=10.0,
        enable_bgm=True
    )
    mixed_audio = AudioFileClip(soundtrack).with_duration(10.0)
    final_video = base_clip.with_audio(mixed_audio)

    # 렌더링
    final_video.write_videofile(
        final_output,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="fast"
    )

    print("\n==================================================")
    print("🎉 화산귀환 10초 시네마틱 영상 제작 완료!")
    print(f"📁 저장 위치: {final_output}")
    print("==================================================")

if __name__ == "__main__":
    run_image_to_video()
