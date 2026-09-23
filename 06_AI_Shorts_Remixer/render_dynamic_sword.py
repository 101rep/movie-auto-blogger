import os
import sys
import numpy as np
import cv2
from PIL import Image
from moviepy import VideoClip, AudioFileClip

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

img_path = "c:/Users/ktaeh/OneDrive/바탕 화면/안티그래비티/분석실/화산귀환_원본.jpg"
out_dir = "c:/Users/ktaeh/OneDrive/바탕 화면/안티그래비티/분석실/분석실완료"
os.makedirs(out_dir, exist_ok=True)
final_output = os.path.join(out_dir, "화산귀환_다이내믹_검기모션_쇼츠.mp4")

img = Image.open(img_path).convert("RGB")
orig_w, orig_h = img.size
target_w, target_h = 1080, 1920

scale = max(target_w / orig_w, target_h / orig_h) * 1.25
nw, nh = int(orig_w * scale), int(orig_h * scale)
base_img = np.array(img.resize((nw, nh), Image.Resampling.LANCZOS))

duration = 10.0
fps = 30

grid_y, grid_x = np.indices((target_h, target_w), dtype=np.float32)

def make_dynamic_frame(t):
    progress = t / duration
    
    # 1. 줌 & 패닝
    zoom = 1.0 + 0.16 * progress
    cur_w, cur_h = int(target_w * zoom), int(target_h * zoom)
    
    x_c = int(nw * 0.5)
    y_c = int(nh * (0.46 + 0.03 * np.sin(progress * np.pi)))
    
    x1 = max(0, x_c - cur_w // 2)
    y1 = max(0, y_c - cur_h // 2)
    x2 = min(nw, x1 + cur_w)
    y2 = min(nh, y1 + cur_h)
    
    cropped = cv2.resize(base_img[y1:y2, x1:x2], (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    
    # 2. 살아 숨쉬는 바람/도포 웨이브 모션
    wave_amp = 8.0 * np.sin(t * 3.5)
    shift_x = (np.sin(grid_y / 40.0 + t * 4.5) * wave_amp * (1.0 - grid_x / target_w)).astype(np.float32)
    shift_y = (np.cos(grid_x / 50.0 + t * 3.0) * (wave_amp * 0.6)).astype(np.float32)
    
    map_x = (grid_x + shift_x).astype(np.float32)
    map_y = (grid_y + shift_y).astype(np.float32)
    warped = cv2.remap(cropped, map_x, map_y, cv2.INTER_LINEAR)
    
    # 3. 검날의 번뜩이는 검기 에너지 파티클
    energy_pulse = (np.sin(t * 10.0) + 1.0) / 2.0
    pt1 = (int(860 - 60 * progress), int(1860 - 80 * progress))
    pt2 = (int(420 - 40 * progress), int(1260 - 60 * progress))
    
    overlay = np.zeros_like(warped)
    thickness = int(14 + 12 * energy_pulse)
    cv2.line(overlay, pt1, pt2, (180, 240, 255), thickness)
    cv2.line(overlay, pt1, pt2, (255, 255, 255), int(thickness * 0.4))
    
    glow = cv2.GaussianBlur(overlay, (41, 41), 0)
    warped = cv2.add(warped, glow)
    
    # 4. 검광 플래시
    for hit_t in [1.8, 4.8, 7.8]:
        diff = t - hit_t
        if 0.0 <= diff < 0.3:
            flash = (1.0 - diff / 0.3) * 55
            warped = np.clip(warped.astype(np.int16) + int(flash), 0, 255).astype(np.uint8)
            
    return warped

print("[Render] 초고속 다이내믹 검기 & 도포 모션 렌더링 시작...")
clip = VideoClip(make_dynamic_frame, duration=duration)

soundtrack = "c:/Users/ktaeh/OneDrive/바탕 화면/안티그래비티/06_AI_Shorts_Remixer/temp/full_soundtrack.mp3"
if os.path.exists(soundtrack):
    audio = AudioFileClip(soundtrack).with_duration(duration)
    clip = clip.with_audio(audio)

clip.write_videofile(
    final_output,
    fps=fps,
    codec="libx264",
    audio_codec="aac",
    threads=4,
    preset="veryfast"
)

print(f"[Render] 완료! 저장 위치: {final_output}")
