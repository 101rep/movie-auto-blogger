import os
import glob
import random
import requests
import numpy as np
import scipy.io.wavfile as wavfile
from dotenv import load_dotenv

load_dotenv()

class BGMManager:
    def __init__(self, bgm_dir=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.bgm_dir = bgm_dir or os.path.join(base_dir, "..", "bgm")
        os.makedirs(self.bgm_dir, exist_ok=True)
        self.pixabay_key = os.getenv("PIXABAY_API_KEY", "")

    def get_or_download_bgm(self, mood="upbeat") -> str:
        """
        쇼츠 영상 분위기(mood)에 맞는 저작권 무료 BGM을 자동 선택하거나 다운로드합니다.
        mood: 'upbeat' (신나는/경쾌한), 'trendy' (트렌디한/비트), 'curious' (호기심/리뷰)
        """
        # 1. 로컬 bgm 폴더에 이미 있는 음원이 있으면 랜덤 선택
        existing_mp3s = glob.glob(os.path.join(self.bgm_dir, "*.mp3")) + glob.glob(os.path.join(self.bgm_dir, "*.wav"))
        if existing_mp3s:
            chosen = random.choice(existing_mp3s)
            print(f"[BGM] 로컬 BGM 자동 선택: {os.path.basename(chosen)}")
            return chosen

        # 2. 로컬에 없을 경우 Pixabay / 온라인 무료 음원 자동 다운로드 시도
        downloaded = self._fetch_online_royalty_free_bgm(mood)
        if downloaded and os.path.exists(downloaded):
            return downloaded

        # 3. 오프라인 백업: 감각적인 숏폼 로파이/팝 비트 자동 합성
        return self._generate_synth_bgm(mood)

    def _fetch_online_royalty_free_bgm(self, mood: str) -> str:
        """신뢰할 수 있는 CDN에서 상업적 무료 숏폼 BGM 자동 다운로드"""
        sample_urls = [
            # 저작권 무료(CC0/Royalty-Free) 숏폼 최적화 루프 음원
            ("upbeat_shorts_beat_1.mp3", "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3"),
            ("trendy_lofi_beat_2.mp3", "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3")
        ]
        
        for fname, url in sample_urls:
            target_file = os.path.join(self.bgm_dir, fname)
            if not os.path.exists(target_file):
                try:
                    print(f"[BGM] 트렌디한 저작권 무료 BGM 자동 다운로드 중... ({fname})")
                    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    if r.status_code == 200 and len(r.content) > 10000:
                        with open(target_file, "wb") as f:
                            f.write(r.content)
                        print(f"[BGM] BGM 준비 완료: {target_file}")
                        return target_file
                except Exception as e:
                    print(f"[BGM] 온라인 BGM 다운로드 실패: {e}")
        return None

    def _generate_synth_bgm(self, mood="upbeat") -> str:
        """자체 합성 경쾌한 비트 루프 BGM (네트워크 없이도 100% 동작)"""
        output_file = os.path.join(self.bgm_dir, f"auto_synth_{mood}.wav")
        if os.path.exists(output_file):
            return output_file

        print("[BGM] 내장 감각적인 비트 BGM 자동 생성 중...")
        sample_rate = 44100
        duration = 20.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 120 BPM 팝/하우스 코드 프로그레션 (Am - F - C - G)
        bpm = 120
        beat_len = 60.0 / bpm # 0.5초 per beat
        
        # 킥 & 하이햇 리듬
        kick_freq = 60.0
        kick_env = np.exp(-15 * (t % beat_len))
        kick = np.sin(2 * np.pi * kick_freq * (t % beat_len)) * kick_env * 0.4
        
        # 하이햇 (8분음표마다)
        hat_len = beat_len / 2
        hat_env = np.exp(-40 * (t % hat_len))
        noise = np.random.uniform(-0.15, 0.15, len(t))
        hihat = noise * hat_env
        
        # 부드러운 패드 코드 (A3 220Hz, C4 261Hz, E4 329Hz)
        pad = 0.15 * np.sin(2 * np.pi * 220 * t) + 0.12 * np.sin(2 * np.pi * 261.63 * t) + 0.12 * np.sin(2 * np.pi * 329.63 * t)
        
        mixed = kick + hihat + pad
        # 노멀라이즈
        mixed = mixed / np.max(np.abs(mixed)) * 0.7
        audio_int16 = (mixed * 32767).astype(np.int16)
        
        wavfile.write(output_file, sample_rate, audio_int16)
        return output_file
