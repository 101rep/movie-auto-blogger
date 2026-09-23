import os
import numpy as np
import scipy.io.wavfile as wavfile
from moviepy import AudioFileClip, CompositeAudioClip
from core.bgm_manager import BGMManager

class SoundFXEngine:
    def __init__(self, temp_dir="temp"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        self.bgm_manager = BGMManager()

    def generate_sfx_files(self):
        sfx_dict = {}
        sample_rate = 44100

        # 1. 후킹 딩(Ding) 사운드
        dur = 0.6
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        tone = 0.5 * np.sin(2 * np.pi * 1046.5 * t) + 0.3 * np.sin(2 * np.pi * 1318.5 * t)
        decay = np.exp(-5 * t)
        ding_audio = (tone * decay * 32767).astype(np.int16)
        ding_path = os.path.join(self.temp_dir, "sfx_ding.wav")
        wavfile.write(ding_path, sample_rate, ding_audio)
        sfx_dict["ding"] = ding_path

        # 2. 화면 전환 슉(Whoosh) 사운드
        dur = 0.35
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        noise = np.random.uniform(-0.5, 0.5, len(t))
        envelope = np.sin(np.pi * t / dur) ** 2
        freq_sweep = np.sin(2 * np.pi * (200 + 1200 * (t / dur)) * t)
        whoosh_audio = ((noise * 0.4 + freq_sweep * 0.3) * envelope * 32767).astype(np.int16)
        whoosh_path = os.path.join(self.temp_dir, "sfx_whoosh.wav")
        wavfile.write(whoosh_path, sample_rate, whoosh_audio)
        sfx_dict["whoosh"] = whoosh_path

        return sfx_dict

    def build_mixed_soundtrack(self, narration_path: str, cut_times: list, total_duration: float, enable_bgm=True) -> str:
        """나레이션 + 효과음(SFX) + AI 자동 배경음악(BGM) 통합 믹싱"""
        sfx_files = self.generate_sfx_files()
        audio_layers = []

        # 1. 자동 BGM 매칭 (볼륨 18%로 은은하게 깔림)
        if enable_bgm:
            try:
                bgm_file = self.bgm_manager.get_or_download_bgm(mood="upbeat")
                if bgm_file and os.path.exists(bgm_file):
                    bgm_clip = AudioFileClip(bgm_file)
                    # 필요한 길이만큼 루프 또는 서브클립
                    if bgm_clip.duration < total_duration:
                        bgm_clip = bgm_clip.with_duration(total_duration)
                    else:
                        bgm_clip = bgm_clip.subclipped(0, total_duration)
                    
                    # 말소리가 잘 들리도록 BGM 볼륨 18%로 세밀하게 조절
                    bgm_clip = bgm_clip.with_volume_scaled(0.18)
                    audio_layers.append(bgm_clip)
                    print(f"[SoundFX] 자동 BGM 결합 완료 ({os.path.basename(bgm_file)}, 볼륨 18%)")
            except Exception as e:
                print(f"[SoundFX] BGM 결합 예외: {e}")

        # 2. 메인 나레이션 (볼륨 100%)
        if narration_path and os.path.exists(narration_path):
            main_narr = AudioFileClip(narration_path).with_volume_scaled(1.0)
            audio_layers.append(main_narr)

        # 3. 사운드 효과음
        ding_clip = AudioFileClip(sfx_files["ding"]).with_start(0.1).with_volume_scaled(0.7)
        audio_layers.append(ding_clip)

        for cut_start in cut_times:
            if cut_start > 0.5 and cut_start < total_duration - 0.5:
                whoosh_clip = AudioFileClip(sfx_files["whoosh"]).with_start(cut_start).with_volume_scaled(0.6)
                audio_layers.append(whoosh_clip)

        # 4. 전체 레이어 합성
        final_audio = CompositeAudioClip(audio_layers).with_duration(total_duration)
        output_soundtrack = os.path.join(self.temp_dir, "full_soundtrack.mp3")
        final_audio.write_audiofile(output_soundtrack, fps=44100, logger=None)
        return output_soundtrack
